import asyncio
import json
import os
import threading
import time
import uuid
import webbrowser
from pathlib import Path
from typing import Dict

from fastapi import (
    BackgroundTasks,
    FastAPI,
    HTTPException,
    Request,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from app.agent.manus import Manus
from app.flow.base import FlowType
from app.flow.flow_factory import FlowFactory
from app.web.log_handler import capture_session_logs, get_logs
from app.web.log_parser import get_all_logs_info, get_latest_log_info, parse_log_file
from app.web.thinking_tracker import ThinkingTracker
from app.agent.llm_wrapper import LLMCallbackWrapper
from app.utils.log_monitor import LogFileMonitor
# from app.web.llm_communication_tracker import LLMCommunicationTracker

# Control whether to automatically open browser (read from environment variable, default to True)
AUTO_OPEN_BROWSER = os.environ.get("AUTO_OPEN_BROWSER", "1") == "1"
last_opened = False  # Track whether browser has been opened

app = FastAPI(title="OpenManus Web")

# Get current file directory
current_dir = Path(__file__).parent
# Set static file directory
app.mount("/static", StaticFiles(directory=current_dir / "static"), name="static")
# Set template directory
templates = Jinja2Templates(directory=current_dir / "templates")

# Store active sessions and their results
active_sessions: Dict[str, dict] = {}

# Store task cancellation events
cancel_events: Dict[str, asyncio.Event] = {}

# Create workspace root directory
WORKSPACE_ROOT = Path(__file__).parent.parent.parent / "workspace"
WORKSPACE_ROOT.mkdir(exist_ok=True)

# Log directory
LOGS_DIR = Path(__file__).parent.parent.parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)


# Store active log monitors
active_log_monitors: Dict[str, LogFileMonitor] = {}


# Create workspace directory function
def create_workspace(session_id: str) -> Path:
    """Create workspace directory for session"""
    # Simplify session_id as directory name
    job_id = f"job_{session_id[:8]}"
    workspace_dir = WORKSPACE_ROOT / job_id
    workspace_dir.mkdir(exist_ok=True)
    return workspace_dir


@app.on_event("startup")
async def startup_event():
    """Startup event: automatically open browser when application starts"""
    global last_opened
    if AUTO_OPEN_BROWSER and not last_opened:
        # Delay 1 second to ensure service has started
        threading.Timer(1.0, lambda: webbrowser.open("http://localhost:8000")).start()
        print("Automatically open browser...")
        last_opened = True


class SessionRequest(BaseModel):
    prompt: str


@app.get("/", response_class=HTMLResponse)
async def get_home(request: Request):
    """Home page entry - use connected interface"""
    return HTMLResponse(
        content=open(
            current_dir / "static" / "connected_interface.html", encoding="utf-8"
        ).read()
    )


@app.get("/original", response_class=HTMLResponse)
async def get_original_interface(request: Request):
    """Original interface entry"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/connected", response_class=HTMLResponse)
async def get_connected_interface(request: Request):
    """Connected backend new interface entry (same as home page)"""
    return HTMLResponse(
        content=open(
            current_dir / "static" / "connected_interface.html", encoding="utf-8"
        ).read()
    )


@app.post("/api/chat")
async def create_chat_session(
    session_req: SessionRequest, background_tasks: BackgroundTasks
):
    session_id = str(uuid.uuid4())
    active_sessions[session_id] = {
        "status": "processing",
        "result": None,
        "log": [],
        "workspace": None,
    }

    # Create cancellation event
    cancel_events[session_id] = asyncio.Event()

    # Create workspace directory
    workspace_dir = create_workspace(session_id)
    active_sessions[session_id]["workspace"] = str(
        workspace_dir.relative_to(WORKSPACE_ROOT)
    )

    background_tasks.add_task(process_prompt, session_id, session_req.prompt)
    return {
        "session_id": session_id,
        "workspace": active_sessions[session_id]["workspace"],
    }


@app.get("/api/chat/{session_id}")
async def get_chat_result(session_id: str):
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    # Use new log processing module to get logs
    session = active_sessions[session_id]
    session["log"] = get_logs(session_id)

    return session


@app.post("/api/chat/{session_id}/stop")
async def stop_processing(session_id: str):
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    if session_id in cancel_events:
        cancel_events[session_id].set()

    active_sessions[session_id]["status"] = "stopped"
    active_sessions[session_id]["result"] = "Processing has been stopped by user"

    return {"status": "stopped"}


@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    try:
        await websocket.accept()

        if session_id not in active_sessions:
            await websocket.send_text(json.dumps({"error": "Session not found"}))
            await websocket.close()
            return

        session = active_sessions[session_id]

        # Register WebSocket send callback function
        async def ws_send(message: str):
            try:
                await websocket.send_text(message)
            except Exception as e:
                print(f"WebSocket send message failed: {str(e)}")

        ThinkingTracker.register_ws_send_callback(session_id, ws_send)

        # Initial status notification with log information
        await websocket.send_text(
            json.dumps(
                {
                    "status": session["status"],
                    "log": session["log"],
                    "thinking_steps": ThinkingTracker.get_thinking_steps(session_id),
                    "logs": ThinkingTracker.get_logs(session_id),  # Add log information
                }
            )
        )

        # Get workspace name (job_id) - prioritize from environment variable
        job_id = None
        # First check current session's workspace association
        if "workspace" in session:
            job_id = session["workspace"]

        # If no log monitor exists, create one
        if session_id not in active_log_monitors and job_id:
            log_path = LOGS_DIR / f"{job_id}.log"
            if log_path.exists():
                log_monitor = LogFileMonitor(job_id)
                log_monitor.start_monitoring()
                active_log_monitors[session_id] = log_monitor

        # Track log updates
        last_log_entries = []
        if job_id and session_id in active_log_monitors:
            last_log_entries = active_log_monitors[session_id].get_log_entries()

        # Wait for result updates
        last_log_count = 0
        last_thinking_step_count = 0
        last_tracker_log_count = 0  # Add ThinkingTracker log count

        while session["status"] == "processing":
            await asyncio.sleep(0.2)  # Decrease check interval to improve real-time performance

            # Check system log updates (new)
            if job_id and session_id in active_log_monitors:
                current_log_entries = active_log_monitors[session_id].get_log_entries()
                if len(current_log_entries) > len(last_log_entries):
                    new_logs = current_log_entries[len(last_log_entries) :]
                    await websocket.send_text(
                        json.dumps(
                            {
                                "status": session["status"],
                                "system_logs": new_logs,
                                # Add a chat_logs field to send system logs as chat messages
                                "chat_logs": new_logs,
                            }
                        )
                    )
                    last_log_entries = current_log_entries

            # Check log updates
            current_log_count = len(session["log"])
            if current_log_count > last_log_count:
                await websocket.send_text(
                    json.dumps(
                        {
                            "status": session["status"],
                            "log": session["log"][last_log_count:],
                        }
                    )
                )
                last_log_count = current_log_count

            # Check thinking step updates
            thinking_steps = ThinkingTracker.get_thinking_steps(session_id)
            current_thinking_step_count = len(thinking_steps)
            if current_thinking_step_count > last_thinking_step_count:
                await websocket.send_text(
                    json.dumps(
                        {
                            "status": session["status"],
                            "thinking_steps": thinking_steps[last_thinking_step_count:],
                        }
                    )
                )
                last_thinking_step_count = current_thinking_step_count

            # Check ThinkingTracker log updates
            tracker_logs = ThinkingTracker.get_logs(session_id)
            current_tracker_log_count = len(tracker_logs)
            if current_tracker_log_count > last_tracker_log_count:
                await websocket.send_text(
                    json.dumps(
                        {
                            "status": session["status"],
                            "logs": tracker_logs[last_tracker_log_count:],
                        }
                    )
                )
                last_tracker_log_count = current_tracker_log_count

            # Check result updates
            if session["result"]:
                await websocket.send_text(
                    json.dumps(
                        {
                            "status": session["status"],
                            "result": session["result"],
                            "log": session["log"][last_log_count:],
                            "thinking_steps": ThinkingTracker.get_thinking_steps(
                                session_id, last_thinking_step_count
                            ),
                            "system_logs": last_log_entries,  # Add system logs
                            "logs": ThinkingTracker.get_logs(
                                session_id, last_tracker_log_count
                            ),  # Add ThinkingTracker logs
                        }
                    )
                )
                break  # Result has been sent, exit loop to avoid duplicate sending

        # Only send final result if loop hasn't been broken due to result
        if not session["result"]:
            await websocket.send_text(
                json.dumps(
                    {
                        "status": session["status"],
                        "result": session["result"],
                        "log": session["log"][last_log_count:],
                        "thinking_steps": ThinkingTracker.get_thinking_steps(
                            session_id, last_thinking_step_count
                        ),
                        "system_logs": last_log_entries,  # Add system logs
                        "logs": ThinkingTracker.get_logs(
                            session_id, last_tracker_log_count
                        ),  # Add ThinkingTracker logs
                    }
                )
            )

        # Unregister WebSocket send callback function
        ThinkingTracker.unregister_ws_send_callback(session_id)
        await websocket.close()
    except WebSocketDisconnect:
        # Client disconnected, normal operation
        ThinkingTracker.unregister_ws_send_callback(session_id)
    except Exception as e:
        # Other exceptions, log but don't interrupt application
        print(f"WebSocket error: {str(e)}")
        ThinkingTracker.unregister_ws_send_callback(session_id)



# Modify file API to support workspace directory
@app.get("/api/files")
async def get_generated_files():
    """Get all workspace directories and files"""
    result = []

    # Get all workspace directories
    workspaces = list(WORKSPACE_ROOT.glob("job_*"))
    workspaces.sort(key=lambda p: p.stat().st_mtime, reverse=True)

    for workspace in workspaces:
        workspace_name = workspace.name
        # Get all files in workspace and sort by modification time
        files = []
        with os.scandir(workspace) as it:
            for entry in it:
                if entry.is_file() and entry.name.split(".")[-1] in [
                    "txt",
                    "md",
                    "html",
                    "css",
                    "js",
                    "py",
                    "json",
                ]:
                    files.append(entry)
        # Sort files by modification time in descending order
        files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

        # If there are files, add the workspace
        if files:
            workspace_item = {
                "name": workspace_name,
                "path": str(workspace.relative_to(Path(__file__).parent.parent.parent)),
                "modified": workspace.stat().st_mtime,
                "files": [],
            }

            # Add files in workspace
            for file in sorted(files, key=lambda p: p.name):
                workspace_item["files"].append(
                    {
                        "name": file.name,
                        "path": str(
                            Path(file.path).relative_to(
                                Path(__file__).parent.parent.parent
                            )
                        ),
                        "type": Path(file.path).suffix[1:],  # Remove dot from extension
                        "size": file.stat().st_size,
                        "modified": file.stat().st_mtime,
                    }
                )

            result.append(workspace_item)

    return {"workspaces": result}


# New log file interface
@app.get("/api/logs")
async def get_system_logs(limit: int = 10):
    """Get system log list"""
    log_files = []
    for entry in os.scandir(LOGS_DIR):
        if entry.is_file() and entry.name.endswith(".log"):
            log_files.append(
                {
                    "name": entry.name,
                    "size": entry.stat().st_size,
                    "modified": entry.stat().st_mtime,
                }
            )
    # Sort log files by modification time in descending order and limit number
    log_files.sort(key=lambda x: x["modified"], reverse=True)
    return {"logs": log_files[:limit]}


@app.get("/api/logs/{log_name}")
async def get_log_content(log_name: str, parsed: bool = False):
    """Get specific log file content"""
    log_path = LOGS_DIR / log_name
    # Safety check
    if not log_path.exists() or not log_path.is_file():
        raise HTTPException(status_code=404, detail="Log file not found")

    # If parsed log information is requested
    if parsed:
        log_info = parse_log_file(str(log_path))
        log_info["name"] = log_name
        return log_info

    # Otherwise return original content
    with open(log_path, "r", encoding="utf-8") as f:
        content = f.read()

    return {"name": log_name, "content": content}


@app.get("/api/logs_parsed")
async def get_parsed_logs(limit: int = 10):
    """Get parsed log information list"""
    return {"logs": get_all_logs_info(str(LOGS_DIR), limit)}


@app.get("/api/logs_parsed/{log_name}")
async def get_parsed_log(log_name: str):
    """Get parsed information of specific log file"""
    log_path = LOGS_DIR / log_name
    # Safety check
    if not log_path.exists() or not log_path.is_file():
        raise HTTPException(status_code=404, detail="Log file not found")

    log_info = parse_log_file(str(log_path))
    log_info["name"] = log_name
    return log_info


@app.get("/api/latest_log")
async def get_latest_log():
    """Get parsed information of latest log file"""
    return get_latest_log_info(str(LOGS_DIR))


@app.get("/api/files/{file_path:path}")
async def get_file_content(file_path: str):
    """Get content of specific file"""
    # Safety check to prevent directory traversal attack
    root_dir = Path(__file__).parent.parent.parent
    full_path = root_dir / file_path

    # Ensure file is within project directory
    try:
        full_path.relative_to(root_dir)
    except ValueError:
        raise HTTPException(status_code=403, detail="Access denied")

    if not full_path.exists() or not full_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")

    # Read file content
    try:
        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Determine file type
        file_type = full_path.suffix[1:] if full_path.suffix else "text"

        return {
            "name": full_path.name,
            "path": file_path,
            "type": file_type,
            "content": content,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")


# Modify process_prompt function to handle workspace
async def process_prompt(session_id: str, prompt: str):
    # Get session workspace
    workspace_dir = None
    if session_id in active_sessions and "workspace" in active_sessions[session_id]:
        workspace_path = active_sessions[session_id]["workspace"]
        workspace_dir = WORKSPACE_ROOT / workspace_path
        os.makedirs(workspace_dir, exist_ok=True)

    # If no workspace, create one
    if not workspace_dir:
        workspace_dir = create_workspace(session_id)
        if session_id in active_sessions:
            active_sessions[session_id]["workspace"] = str(
                workspace_dir.relative_to(WORKSPACE_ROOT)
            )

    # Set current working directory to workspace
    original_cwd = os.getcwd()
    os.chdir(workspace_dir)

    # Use workspace name as log file name prefix
    job_id = workspace_dir.name
    # Set log file path
    task_log_path = LOGS_DIR / f"{job_id}.log"

    # Create log monitor and start monitoring
    log_monitor = LogFileMonitor(job_id)
    observer = log_monitor.start_monitoring()
    active_log_monitors[session_id] = log_monitor

    async def sync_logs():
        """Periodically get logs from LogFileMonitor and update to ThinkingTracker in real-time"""
        last_count = 0
        try:
            while True:
                if session_id not in active_log_monitors:
                    break
                current_logs = active_log_monitors[session_id].get_log_entries()
                if len(current_logs) > last_count:
                    # Process new log entries
                    new_logs = current_logs[last_count:]
                    # Process each new log entry individually to ensure real-time performance
                    for log_entry in new_logs:
                        # Add each log entry to ThinkingTracker individually
                        ThinkingTracker.add_log_entry(
                            session_id,
                            {
                                "level": log_entry.get("level", "INFO"),
                                "message": log_entry.get("message", ""),
                                "timestamp": log_entry.get("timestamp", time.time()),
                            },
                        )
                    last_count = len(current_logs)
                # Decrease polling interval to improve real-time performance
                await asyncio.sleep(0.1)  # Check every 0.1 seconds
        except Exception as e:
            print(f"Error syncing logs: {str(e)}")

    # Start log synchronization task
    sync_task = asyncio.create_task(sync_logs())

    # Set environment variable to inform logger to use this log file, ensuring both methods are set
    os.environ["OPENMANUS_LOG_FILE"] = str(task_log_path)
    os.environ["OPENMANUS_TASK_ID"] = job_id

    try:
        # Use log capture context manager to parse log level and content
        with capture_session_logs(session_id) as log:
            # Initialize thinking tracking
            ThinkingTracker.start_tracking(session_id)
            ThinkingTracker.add_thinking_step(session_id, "Start processing user requests")
            ThinkingTracker.add_thinking_step(
                session_id, f"workspace directory: {workspace_dir.name}"
            )

            # Directly record user input prompt
            ThinkingTracker.add_communication(session_id, "user prompt", prompt)

            # Initialize agent and task flow
            ThinkingTracker.add_thinking_step(session_id, "Initialize AI agent and task flow")
            agent = Manus()

            # Use wrapper to wrap LLM
            if hasattr(agent, "llm"):
                original_llm = agent.llm
                wrapped_llm = LLMCallbackWrapper(original_llm)

                # Register callback functions
                def on_before_request(data):
                    # Extract request content
                    prompt_content = None
                    if data.get("args") and len(data["args"]) > 0:
                        prompt_content = str(data["args"][0])
                    elif data.get("kwargs") and "prompt" in data["kwargs"]:
                        prompt_content = data["kwargs"]["prompt"]
                    else:
                        prompt_content = str(data)

                    # Record communication content
                    print(f"Send to LLM: {prompt_content[:100]}...")
                    ThinkingTracker.add_communication(
                        session_id, "Send to LLM", prompt_content
                    )

                def on_after_request(data):
                    # Extract response content
                    response = data.get("response", "")
                    response_content = ""

                    # Try to extract text content from different formats
                    if isinstance(response, str):
                        response_content = response
                    elif isinstance(response, dict):
                        if "content" in response:
                            response_content = response["content"]
                        elif "text" in response:
                            response_content = response["text"]
                        else:
                            response_content = str(response)
                    elif hasattr(response, "content"):
                        response_content = response.content
                    else:
                        response_content = str(response)

                    # Record communication content
                    print(f"Received from LLM: {response_content[:100]}...")
                    ThinkingTracker.add_communication(
                        session_id, "Received from LLM", response_content
                    )

                # Register callbacks
                wrapped_llm.register_callback("before_request", on_before_request)
                wrapped_llm.register_callback("after_request", on_after_request)

                # Replace original LLM
                agent.llm = wrapped_llm

            flow = FlowFactory.create_flow(
                flow_type=FlowType.PLANNING,
                agents=agent,
            )

            # Record processing start
            ThinkingTracker.add_thinking_step(
                session_id, f"Analyze user requests: {prompt[:50]}{'...' if len(prompt) > 50 else ''}"
            )
            log.info(f"Start execution: {prompt[:50]}{'...' if len(prompt) > 50 else ''}")

            # Check if task has been cancelled
            cancel_event = cancel_events.get(session_id)
            if cancel_event and cancel_event.is_set():
                log.warning("Processing has been cancelled by the user")
                ThinkingTracker.mark_stopped(session_id)
                active_sessions[session_id]["status"] = "stopped"
                active_sessions[session_id]["result"] = "Processing has been stopped by the user"
                return

            # Check existing files in workspace before execution
            existing_files = set()
            for ext in ["*.txt", "*.md", "*.html", "*.css", "*.js", "*.py", "*.json"]:
                existing_files.update(f.name for f in workspace_dir.glob(ext))

            # Track plan creation process
            ThinkingTracker.add_thinking_step(session_id, "Create a task execution plan")
            ThinkingTracker.add_thinking_step(session_id, "Start executing the task plan")

            # Get cancellation event to pass to flow.execute
            cancel_event = cancel_events.get(session_id)

            # Initial check, if cancelled do not execute
            if cancel_event and cancel_event.is_set():
                log.warning("Processing has been cancelled by the user")
                ThinkingTracker.mark_stopped(session_id)
                active_sessions[session_id]["status"] = "stopped"
                active_sessions[session_id]["result"] = "Processing has been stopped by the user"
                return

            # Execute actual processing - pass job_id and cancel_event to flow.execute method
            result = await flow.execute(prompt, job_id, cancel_event)

            # Check new files generated after execution
            new_files = set()
            for ext in ["*.txt", "*.md", "*.html", "*.css", "*.js", "*.py", "*.json"]:
                new_files.update(f.name for f in workspace_dir.glob(ext))
            newly_created = new_files - existing_files

            if newly_created:
                files_list = ", ".join(newly_created)
                ThinkingTracker.add_thinking_step(
                    session_id,
                    f"{len(newly_created)} files are generated in the workspace {workspace_dir.name}. Files: {files_list}",
                )
                # Add file list to session result
                active_sessions[session_id]["generated_files"] = list(newly_created)

            # Record completion
            log.info("Processing completed")
            ThinkingTracker.add_conclusion(
                session_id, f"Task processing completed! Results generated in workspace {workspace_dir.name}."
            )

            active_sessions[session_id]["status"] = "completed"
            active_sessions[session_id]["result"] = result
            active_sessions[session_id][
                "thinking_steps"
            ] = ThinkingTracker.get_thinking_steps(session_id)

    except asyncio.CancelledError:
        # Handle cancellation
        print("Processing cancelled")
        ThinkingTracker.mark_stopped(session_id)
        active_sessions[session_id]["status"] = "stopped"
        active_sessions[session_id]["result"] = "Processing has been cancelled"
    except Exception as e:
        # Handle error
        error_msg = f"Processing error: {str(e)}"
        print(error_msg)
        ThinkingTracker.add_error(session_id, f"Handle encountered errors: {str(e)}")
        active_sessions[session_id]["status"] = "error"
        active_sessions[session_id]["result"] = f"An error occurred: {str(e)}"
    finally:
        # Restore original working directory
        os.chdir(original_cwd)

        # Clear log file environment variable
        if "OPENMANUS_LOG_FILE" in os.environ:
            del os.environ["OPENMANUS_LOG_FILE"]
        if "OPENMANUS_TASK_ID" in os.environ:
            del os.environ["OPENMANUS_TASK_ID"]

        # Clean up resources
        if (
            "agent" in locals()
            and hasattr(agent, "llm")
            and isinstance(agent.llm, LLMCallbackWrapper)
        ):
            try:
                # Correctly remove callbacks
                if "on_before_request" in locals():
                    agent.llm._callbacks["before_request"].remove(on_before_request)
                if "on_after_request" in locals():
                    agent.llm._callbacks["after_request"].remove(on_after_request)
            except (ValueError, Exception) as e:
                print(f"Error cleaning up callback: {str(e)}")

        # Clear cancellation event
        if session_id in cancel_events:
            del cancel_events[session_id]

        # If monitor exists, stop monitoring
        if session_id in active_log_monitors:
            observer.stop()
            observer.join(timeout=1)
            del active_log_monitors[session_id]

        # Cancel log synchronization task
        if sync_task:
            sync_task.cancel()
            try:
                await sync_task
            except asyncio.CancelledError:
                pass


# Add new API endpoint to get thinking steps
@app.get("/api/thinking/{session_id}")
async def get_thinking_steps(session_id: str, start_index: int = 0):
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    return {
        "status": ThinkingTracker.get_status(session_id),
        "thinking_steps": ThinkingTracker.get_thinking_steps(session_id, start_index),
    }


# Add API endpoint to get progress information
@app.get("/api/progress/{session_id}")
async def get_progress(session_id: str):
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    return ThinkingTracker.get_progress(session_id)


# Add API endpoint to get system logs for specific session
@app.get("/api/systemlogs/{session_id}")
async def get_system_logs(session_id: str):
    """Get system logs for specific session"""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    job_id = None
    if "workspace" in active_sessions[session_id]:
        workspace_path = active_sessions[session_id]["workspace"]
        job_id = workspace_path

    if not job_id:
        return {"logs": []}

    # If monitor exists, use monitor
    if session_id in active_log_monitors:
        logs = active_log_monitors[session_id].get_log_entries()
        return {"logs": logs}

    # Otherwise read log file directly
    log_path = LOGS_DIR / f"{job_id}.log"
    if not log_path.exists():
        return {"logs": []}

    try:
        with open(log_path, "r", encoding="utf-8") as f:
            logs = [line.strip() for line in f.readlines()]
        return {"logs": logs}
    except Exception as e:
        return {"error": f"Error reading log file: {str(e)}"}

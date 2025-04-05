# OpenManus Web Application

This is the Web interface part of the OpenManus project, providing a friendly user interface that allows users to interact with the OpenManus AI assistant directly in the browser.

![OpenManus Web Interface](../assets/interface.png)

## Main Features

- 🌐 Modern Web interface with real-time communication support
- 💬 Intuitive chat interface for asking questions and getting AI responses
- 🧠 Visualized thinking process showing each step of AI's thought process
- 📁 Workspace file management for viewing and managing AI-generated files
- 📊 Detailed log tracking and monitoring
- 🚀 Support for interrupting and stopping ongoing requests

## Tech Stack

- **Backend**: FastAPI, Python, WebSocket
- **Frontend**: HTML, CSS, JavaScript
- **Communication**: Real-time WebSocket communication
- **Storage**: File system storage for generated files and logs

## Quick Start

1. Ensure all dependencies are installed:

```bash
pip install -r requirements.txt
```

2. Start the Web server:

```bash
python web_run.py
```
Or from the project root directory:

```bash
python main.py --web
```

3. Open browser and visit: http://localhost:8000

## Project Structure

```
app/web/
├── app.py               # Web application entry point, FastAPI application instance
├── log_handler.py       # Log handling module
├── log_parser.py        # Log parser
├── thinking_tracker.py  # Thinking process tracker
├── static/              # Static resource folder (JS, CSS)
│   ├── connected_interface.html # Main interface HTML
│   ├── connected_interface.js   # Main interface JavaScript
│   └── ...                      # Other static resources
└── templates/           # Jinja2 template folder
```

## API Endpoints

### Chat Related

- `POST /api/chat` - Create new chat session
- `GET /api/chat/{session_id}` - Get specific session results
- `POST /api/chat/{session_id}/stop` - Stop processing of specific session
- `WebSocket /ws/{session_id}` - Establish WebSocket connection with session

### File Related

- `GET /api/files` - Get all workspace directories and files
- `GET /api/files/{file_path}` - Get content of specific file

### Log Related 

- `GET /api/logs` - Get system log list
- `GET /api/logs/{log_name}` - Get content of specific log file
- `GET /api/logs_parsed` - Get parsed log information list
- `GET /api/logs_parsed/{log_name}` - Get parsed log information of specific log file
- `GET /api/latest_log` - Get latest log file's parsed information
- `GET /api/systemlogs/{session_id}` - Get system logs for specific session

### Thinking Process

- `GET /api/thinking/{session_id}` - Get specific session's thinking steps
- `GET /api/progress/{session_id}` - Get progress information of specific session

## Interface Description

The OpenManus Web interface is divided into two main parts:

1. **Left Panel** - Display AI thinking process and workspace files
   - AI Thinking Timeline: Display each step of AI processing
   - Workspace Files: Display AI-generated files, click to view content

2. **Right Panel** - Chat interface
   - Chat History: Display user and AI conversation
   - Input Area: User can input questions or instructions

## Local Development

1. Clone the repository
2. Install dependencies
3. Start the application in development mode:

```bash
uvicorn app.web.app:app --reload
```
Or
```bash
python web_run.py
```

## Contribution

Welcome to contribute code, report issues, or suggest improvements. Please create an issue or submit a pull request.

## License

This project uses [Open Source License], see the LICENSE file in the root directory of the project.

## Technical Support

If you have any questions or need help, please create a GitHub Issue.
import argparse
import os
import sys
from pathlib import Path

import uvicorn


# Check WebSocket dependencies
def check_websocket_dependencies():
    pass

    return True


# Make sure the directory structure exists
def ensure_directories():
    # Create a templates directory
    templates_dir = Path("app/web/templates")
    templates_dir.mkdir(parents=True, exist_ok=True)

    # Create static directory
    static_dir = Path("app/web/static")
    static_dir.mkdir(parents=True, exist_ok=True)

    # Make sure the __init__.py file exists
    init_file = Path("app/web/__init__.py")
    if not init_file.exists():
        init_file.touch()


if __name__ == "__main__":
    # Add command line parameters
    parser = argparse.ArgumentParser(description="OpenManus Web Application Server")
    parser.add_argument("--no-browser", action="store_true", help="Do not automatically open the browser on startup")
    parser.add_argument("--port", type=int, default=8000, help="Server listening port number (default: 8000)")

    args = parser.parse_args()

    ensure_directories()

    if not check_websocket_dependencies():
        print("Exit the application. Please install necessary dependencies and try again.")
        sys.exit(1)

    # Set environment variables to control whether to automatically open the browser
    if args.no_browser:
        os.environ["AUTO_OPEN_BROWSER"] = "0"
    else:
        os.environ["AUTO_OPEN_BROWSER"] = "1"

    port = args.port

    print(f"🚀 The OpenManus web application is starting up...")
    print(f"Open http://localhost:{port} to get started")

    uvicorn.run("app.web.app:app", host="0.0.0.0", port=port, reload=True)

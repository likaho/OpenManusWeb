```mermaid
classDiagram
    class WebApplication {
        +app: FastAPI
        +routes: List[Route]
        +mount()
        +websocket()
    }

    class WebSocketManager {
        +active_connections: List[WebSocket]
        +connect()
        +disconnect()
        +broadcast()
    }

    class LogHandler {
        +capture_session_logs()
        +get_logs()
    }

    class ThinkingTracker {
        +track_thinking()
        +get_thinking_steps()
    }

    class LogParser {
        +parse_log()
        +get_parsed_logs()
    }

    class StaticFiles {
        +mount_static()
        +serve_files()
    }

    WebApplication --> WebSocketManager
    WebApplication --> LogHandler
    WebApplication --> ThinkingTracker
    WebApplication --> LogParser
    WebApplication --> StaticFiles

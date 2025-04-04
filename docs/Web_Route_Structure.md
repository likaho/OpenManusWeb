```mermaid
classDiagram
    class WebApplication {
        +app: FastAPI
        +routes: List[Route]
        +mount()
        +websocket()
    }

    class APIEndpoints {
        +chat()
        +files()
        +logs()
        +thinking()
    }

    class WebSocketRoutes {
        +websocket_endpoint()
        +handle_messages()
    }

    class StaticRoutes {
        +static_files()
        +templates()
    }

    class TemplateHandlers {
        +render_template()
        +load_templates()
    }

    WebApplication --> APIEndpoints
    WebApplication --> WebSocketRoutes
    WebApplication --> StaticRoutes
    WebApplication --> TemplateHandlers
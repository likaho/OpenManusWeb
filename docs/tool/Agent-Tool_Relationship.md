```mermaid
classDiagram
    class Manus {
        +name: "Manus"
        +description: "Versatile agent with multiple tools"
        +available_tools: ToolCollection
    }

    class ToolCollection {
        +tools: List[Tool]
        +get_tool()
        +execute_tool()
    }

    class Tool {
        +name: str
        +description: str
        +execute()
    }

    class GoogleSearch {
        +query: str
        +num_results: int
        +execute()
    }

    class BrowserUseTool {
        +url: str
        +execute()
    }

    class FileSaver {
        +file_path: str
        +content: str
        +execute()
    }

    class PythonExecute {
        +code: str
        +execute()
    }

    Manus --> ToolCollection
    ToolCollection --> Tool
    ToolCollection --> GoogleSearch
    ToolCollection --> BrowserUseTool
    ToolCollection --> FileSaver
    ToolCollection --> PythonExecute

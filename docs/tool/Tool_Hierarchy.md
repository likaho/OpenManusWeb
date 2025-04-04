```mermaid
classDiagram
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

    Tool <|-- GoogleSearch
    Tool <|-- BrowserUseTool
    Tool <|-- FileSaver
    Tool <|-- PythonExecute

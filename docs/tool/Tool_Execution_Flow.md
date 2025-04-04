```mermaid
sequenceDiagram
    participant Client
    participant Manus
    participant ToolCollection
    participant GoogleSearch
    participant BrowserUseTool
    participant FileSaver
    participant PythonExecute

    Client->>Manus: Request with task
    Manus->>ToolCollection: Get appropriate tool
    alt Task requires search
        ToolCollection->>GoogleSearch: execute(query)
        GoogleSearch-->>ToolCollection: Return search results
    else Task requires web
        ToolCollection->>BrowserUseTool: execute(url)
        BrowserUseTool-->>ToolCollection: Return web content
    else Task requires file
        ToolCollection->>FileSaver: execute(file_path, content)
        FileSaver-->>ToolCollection: Return file status
    else Task requires code
        ToolCollection->>PythonExecute: execute(code)
        PythonExecute-->>ToolCollection: Return execution result
    end

    ToolCollection-->>Manus: Return tool result
    Manus-->>Client: Return processed response
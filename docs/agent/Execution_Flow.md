```mermaid
sequenceDiagram
    participant Client
    participant Manus
    participant ToolCallAgent
    participant ReActAgent
    participant ToolCollection
    participant Tool

    Client->>Manus: Request with task
    Manus->>ToolCallAgent: Initialize with tools
    ToolCallAgent->>ReActAgent: Plan execution
    ReActAgent->>ToolCallAgent: Get next step
    ToolCallAgent->>ToolCollection: Select appropriate tool
    ToolCollection->>Tool: Execute tool
    Tool-->>ToolCollection: Return result
    ToolCollection-->>ToolCallAgent: Return tool result
    ToolCallAgent-->>ReActAgent: Update plan
    ReActAgent-->>Manus: Return final result
    Manus-->>Client: Return processed response
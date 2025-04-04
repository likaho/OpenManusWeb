```mermaid
graph TD
    %% Nodes
    Manus[Manus Agent] -->|Uses| ToolCallAgent[ToolCallAgent]
    ToolCallAgent -->|Extends| PlanningAgent[PlanningAgent]
    
    %% Tool Collection
    ToolCollection[ToolCollection] -->|Includes| BrowserUseTool[BrowserUseTool]
    ToolCollection -->|Includes| FileSaver[FileSaver]
    ToolCollection -->|Includes| GoogleSearch[GoogleSearch]
    ToolCollection -->|Includes| PythonExecute[PythonExecute]
    ToolCollection -->|Includes| Terminate[Terminate]
    
    %% Flow of Control
    Manus -->|Uses| ToolCollection
    Manus -->|Uses| NEXT_STEP_PROMPT[NEXT_STEP_PROMPT]
    Manus -->|Uses| SYSTEM_PROMPT[SYSTEM_PROMPT]
    
    %% Styling
    classDef agent fill:#f9f,stroke:#333,stroke-width:2px
    classDef tool fill:#bbf,stroke:#333,stroke-width:2px
    classDef prompt fill:#bfb,stroke:#333,stroke-width:2px
    
    class Manus,ToolCallAgent,PlanningAgent agent
    class BrowserUseTool,FileSaver,GoogleSearch,PythonExecute,Terminate tool
    class NEXT_STEP_PROMPT,SYSTEM_PROMPT prompt
```mermaid
sequenceDiagram
    participant Client
    participant FlowFactory
    participant PlanningFlow
    participant LLM
    participant PlanningTool
    participant BaseAgent
    participant Message

    Client->>FlowFactory: Request flow creation
    FlowFactory->>PlanningFlow: Create PlanningFlow instance
    PlanningFlow->>LLM: Initialize LLM
    PlanningFlow->>PlanningTool: Initialize PlanningTool
    PlanningFlow->>Message: Create system message
    PlanningFlow->>Message: Create user message
    PlanningFlow->>LLM: ask_tool()
    LLM->>PlanningTool: Execute planning
    PlanningTool-->>PlanningFlow: Return plan
    PlanningFlow->>BaseAgent: Get executor
    BaseAgent-->>PlanningFlow: Execute step
    PlanningFlow-->>Client: Return result
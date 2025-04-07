```mermaid
sequenceDiagram
    participant Client
    participant PlanningFlow
    participant SWEAgent
    participant BrowserTool
    participant PythonExecute
    participant FileTools

    Client->>PlanningFlow: Receive plan result
    PlanningFlow->>PlanningFlow: Identify next step
    PlanningFlow->>PlanningFlow: Select appropriate agent (SWEAgent)
    PlanningFlow->>SWEAgent: Pass step details
    SWEAgent->>SWEAgent: Analyze step requirements
    SWEAgent->>BrowserTool: Use browser tools (if needed)
    BrowserTool->>SWEAgent: Return web data
    SWEAgent->>PythonExecute: Execute code (if needed)
    PythonExecute->>SWEAgent: Return execution results
    SWEAgent->>FileTools: Create/modify files (if needed)
    FileTools->>SWEAgent: Return file status
    SWEAgent->>PlanningFlow: Update step status
    PlanningFlow->>PlanningFlow: Mark step as completed
    PlanningFlow->>Client: Update UI with progress
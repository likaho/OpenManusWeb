```mermaid
graph TD
    A[User Layer]
    A --> B["main.py (Terminal)"]
    A --> C[run_mcp.py]
    A --> D["run_flow.py (Multi-Agent)"]

    E[Core System Layer]
    E --> F["Configuration (config.toml)"]
    E --> G["Prompt System (/src/prompts/)"]
    E --> H["Agent System (LangGraph)"]
    E --> I[Tools Integration]

    J[Agent Layer]
    J --> K[Coordinator]
    J --> L[Planner]
    J --> M[Executor]
    J --> N[Monitor]

    O[Tools Layer]
    O --> P[File Management]
    O --> Q[Code Execution]
    O --> R[Web Interaction]
    O --> S[Data Processing]

    T[External Services Layer]
    T --> U["OpenAI API (GPT-4, etc.)"]
    T --> V[Other External Services/APIs]

    A --> E
    E --> J
    J --> O
    O --> T

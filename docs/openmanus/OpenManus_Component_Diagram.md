```mermaid
graph TD
    A[OpenManus System]
    A --> B[User Interface]
    A --> C[Configuration Management System]
    B --> C
    A --> D[Core Agent System]
    A --> E[Prompt Management System]
    D --> E
    A --> F[Agent Components]
    F --> G[Coordinator]
    F --> H[Planner]
    F --> I[Executor]
    F --> J[Monitor]
    A --> K[Tool Registry & Manager]
    G --> K
    H --> K
    I --> K
    J --> K
    A --> L[LLM Client Interface]
    A --> M[File Management Tool]
    L --> M
    A --> N[External API Service OpenAI]
    A --> O[Code Execution Tool]
    A --> P[Web Interaction Tool Playwright]
    A --> Q[Data Processing Tool]

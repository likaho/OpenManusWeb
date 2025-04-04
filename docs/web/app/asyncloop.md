```mermaid
sequenceDiagram
    participant API as app.py
    participant Session
    participant AsyncLoop

    API->>Session: Check status
    loop While processing
        API->>AsyncLoop: sleep(0.2)
        API->>FileSystem: Check log updates
        API->>Session: Update status
    end
    Session-->>API: Return final status
    API-->>Client: Return final response
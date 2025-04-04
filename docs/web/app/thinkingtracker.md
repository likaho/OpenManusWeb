```mermaid
sequenceDiagram
    participant Client
    participant API as app.py
    participant ThinkingTracker
    participant FileSystem

    Client->>API: Request with job_id
    API->>ThinkingTracker: Check tracking status
    alt Tracking needed
        API->>FileSystem: Check log file
        FileSystem-->>API: Return file status
        API->>ThinkingTracker: Start tracking
        ThinkingTracker->>ThinkingTracker: Monitor logs
    else
        ThinkingTracker-->>API: Return current status
    end

    ThinkingTracker->>FileSystem: Read log updates
    FileSystem-->>ThinkingTracker: Return updates
    ThinkingTracker->>API: Process updates
    API-->>Client: Return processed data
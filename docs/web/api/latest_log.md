```mermaid
sequenceDiagram
    participant Client
    participant API as /api/latest_log
    participant FileSystem
    participant LogParser

    Client->>API: GET /api/latest_log
    API->>FileSystem: Get latest log file
    FileSystem-->>API: Return latest log path
    API->>LogParser: get_latest_log_info(logs_dir)
    LogParser-->>API: Return parsed log info
    API-->>Client: Return latest log info
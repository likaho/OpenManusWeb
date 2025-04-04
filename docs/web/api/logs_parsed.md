```mermaid
sequenceDiagram
    participant Client
    participant API as /api/logs_parsed/{log_name}
    participant FileSystem
    participant LogParser

    Client->>API: GET /api/logs_parsed/{log_name}
    API->>FileSystem: Check if log file exists
    alt File exists
        FileSystem-->>API: Return file path
        API->>LogParser: parse_log_file(log_path)
        LogParser-->>API: Return parsed log info
        API-->>Client: Return log_info with name
    else File not found
        FileSystem-->>API: Return 404
        API-->>Client: Return 404 Not Found
    end
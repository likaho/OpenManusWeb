```mermaid
sequenceDiagram
    participant Client
    participant API as app.py
    participant LogMonitor as LogFileMonitor
    participant FileSystem
    participant ActiveMonitors as active_log_monitors

    Client->>API: Request with job_id
    API->>ActiveMonitors: Check session_id exists
    alt No existing monitor
        API->>FileSystem: Check log file exists
        alt File exists
            FileSystem-->>API: Return file path
            API->>LogMonitor: Create new LogFileMonitor
            LogMonitor->>LogMonitor: start_monitoring()
            API->>ActiveMonitors: Store monitor
        else
            FileSystem-->>API: Return false
        end
    else
        ActiveMonitors-->>API: Return existing monitor
    end

    API->>LogMonitor: get_log_entries()
    LogMonitor-->>API: Return log entries
    API-->>Client: Return log entries
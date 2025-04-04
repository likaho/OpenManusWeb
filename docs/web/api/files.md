```mermaid
sequenceDiagram
    participant Client
    participant API as /api/files/{file_path}
    participant FileSystem

    Client->>API: GET /api/files/{file_path}
    API->>FileSystem: Get file content
    FileSystem-->>API: Return file content
    API-->>Client: Return file content
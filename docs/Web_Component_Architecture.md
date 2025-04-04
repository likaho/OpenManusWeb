```mermaid
sequenceDiagram
    participant Client
    participant WebApp
    participant WebSocket
    participant LogHandler
    participant ThinkingTracker
    participant LogParser

    Client->>WebApp: Request connection
    WebApp->>WebSocket: Create connection
    WebSocket->>WebApp: Register connection

    Client->>WebApp: Send message
    WebApp->>ThinkingTracker: Track thinking
    ThinkingTracker->>LogHandler: Capture logs
    LogHandler->>LogParser: Parse logs
    LogParser->>WebApp: Return parsed logs
    WebApp->>WebSocket: Send response
    WebSocket->>Client: Receive response

    Client->>WebSocket: Disconnect
    WebSocket->>WebApp: Remove connection
    WebApp->>LogHandler: Clean up logs
```mermaid
classDiagram
    class ToolCallAgent {
        +available_tools: ToolCollection
        +tool_choices: str
        +special_tool_names: List[str]
        +tool_calls: List[ToolCall]
        +execute()
        +plan()
    }

    class ToolCollection {
        +tools: List[Tool]
        +get_tool()
        +execute_tool()
    }

    class Tool {
        +name: str
        +description: str
        +execute()
    }

    class CreateChatCompletion
    class Terminate

    ToolCallAgent --> ToolCollection
    ToolCollection --> Tool
    ToolCollection --> CreateChatCompletion
    ToolCollection --> Terminate
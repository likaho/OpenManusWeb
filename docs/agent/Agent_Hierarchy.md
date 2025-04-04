```mermaid
classDiagram
    class Agent {
        +name: str
        +description: str
        +system_prompt: str
        +next_step_prompt: str
    }

    class ReActAgent {
        +execute()
        +plan()
    }

    class ToolCallAgent {
        +available_tools: ToolCollection
        +tool_choices: str
        +special_tool_names: List[str]
        +tool_calls: List[ToolCall]
    }

    class Manus {
        +name: "Manus"
        +description: "Versatile agent with multiple tools"
    }

    Agent <|-- ReActAgent
    ReActAgent <|-- ToolCallAgent
    ToolCallAgent <|-- Manus


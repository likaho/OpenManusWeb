```mermaid
classDiagram
    class BaseFlow {
        +llm: LLM
        +planning_tool: PlanningTool
        +executor_keys: List[str]
        +active_plan_id: str
        +current_step_index: int
        +execute()
        +get_executor()
    }

    class PlanningFlow {
        +_create_initial_plan()
        +_get_current_step_info()
        +_execute_step()
        +_finalize_plan()
    }

    class FlowFactory {
        +create_flow()
    }

    class LLM {
        +ask_tool()
    }

    class PlanningTool {
        +execute()
    }

    class BaseAgent {
        +state: AgentState
    }

    class Message {
        +system_message()
        +user_message()
    }

    BaseFlow <|-- PlanningFlow
    BaseFlow --> LLM
    BaseFlow --> PlanningTool
    BaseFlow --> BaseAgent
    BaseFlow --> Message
    FlowFactory --> BaseFlow
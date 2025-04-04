```mermaid
classDiagram
    class PlanningFlow {
        +execute()
        +_create_initial_plan()
        +_get_current_step_info()
        +_execute_step()
        +_finalize_plan()
    }

    class FlowComponents {
        +llm: LLM
        +planning_tool: PlanningTool
        +executor_keys: List[str]
        +active_plan_id: str
        +current_step_index: int
    }

    class FlowMethods {
        +get_executor()
        +_create_initial_plan()
        +_get_current_step_info()
        +_execute_step()
        +_finalize_plan()
    }

    class FlowLifecycle {
        +initialize()
        +plan()
        +execute()
        +finalize()
    }

    PlanningFlow --> FlowComponents
    PlanningFlow --> FlowMethods
    PlanningFlow --> FlowLifecycle
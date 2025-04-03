"""
Add thinking process tracking functionality to the flow
"""
from functools import wraps

from app.web.thinking_tracker import ThinkingTracker


class FlowTracker:
    """Flow tracker for hooking into flow execution process and adding thinking step records"""

    @staticmethod
    def patch_flow(flow_obj, session_id: str):
        """Apply tracking patches to the flow object"""
        if not hasattr(flow_obj, "_original_execute"):
            # Save the original method
            flow_obj._original_execute = flow_obj.execute

            # Add session ID
            flow_obj._tracker_session_id = session_id

            # Replace the execute method
            @wraps(flow_obj._original_execute)
            async def tracked_execute(prompt, *args, **kwargs):
                # Add thinking step before execution
                ThinkingTracker.add_thinking_step(session_id, "Start executing the flow")

                # Track sub-step execution
                if hasattr(flow_obj, "_execute_step"):
                    original_step = flow_obj._execute_step

                    @wraps(original_step)
                    async def tracked_step():
                        if hasattr(flow_obj, "current_step_description"):
                            step_desc = flow_obj.current_step_description
                            ThinkingTracker.add_thinking_step(
                                session_id, f"Executing step: {step_desc}"
                            )
                        else:
                            ThinkingTracker.add_thinking_step(session_id, "Executing flow step")

                        result = await original_step()
                        return result

                    flow_obj._execute_step = tracked_step

                # Execute the original method
                result = await flow_obj._original_execute(prompt, *args, **kwargs)

                # Add thinking step after execution
                ThinkingTracker.add_thinking_step(session_id, "Flow execution completed")

                return result

            flow_obj.execute = tracked_execute

            return True
        return False

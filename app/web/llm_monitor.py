# """
# LLM communication monitor module, used to capture and simulate LLM communication content
# """
# import asyncio
# import random
# import time
# from functools import wraps
# from typing import Any, Callable, Dict, List, Optional


# class LLMMonitor:
#     """LLM communication monitor, supports multiple ways to track LLM communication"""

#     def __init__(self):
#         self.interceptors = []
#         self.communications = []

#     def register_interceptor(self, func: Callable):
#         """Register an interceptor function that will be called on each communication"""
#         self.interceptors.append(func)
#         return func  #Easy to use as a decorator

#     def record_communication(self, direction: str, content: Any):
#         """Record communication content"""
#         comm_record = {
#             "direction": direction,  # "in" or "out"
#             "content": str(content)[:1000],  # Limit length
#             "timestamp": time.time(),
#         }
#         self.communications.append(comm_record)

#         # Notify all interceptors
#         for interceptor in self.interceptors:
#             try:
#                 interceptor(comm_record)
#             except Exception as e:
#                 print(f"Interceptor error: {str(e)}")

#     def get_communications(self, start_idx: int = 0) -> List[Dict[str, Any]]:
#         """Get communication records"""
#         return self.communications[start_idx:]

#     def clear(self):
#         """Clear all communication records"""
#         self.communications = []

#     def intercept_method(self, obj, method_name):
#         """Intercept object method calls"""
#         if not hasattr(obj, method_name):
#             return False

#         original_method = getattr(obj, method_name)

#         @wraps(original_method)
#         async def wrapped_method(*args, **kwargs):
#             # Record input
#             input_data = str(args[0]) if args else str(kwargs)
#             self.record_communication("in", input_data)

#             # Call original method
#             result = await original_method(*args, **kwargs)

#             # Record output
#             self.record_communication("out", result)
#             return result

#         # Replace original method
#         setattr(obj, method_name, wrapped_method)
#         return True


# # Create a global monitor instance
# monitor = LLMMonitor()


# # Provide some mock LLM functions for demonstration or testing
# async def simulate_llm_thinking(
#     prompt: str, callback: Optional[Callable] = None, steps: int = 5, delay: float = 1.0
# ):
#     """Simulate LLM thinking process, generating a series of thinking steps"""

#     # Record input
#     monitor.record_communication("in", prompt)

#     thinking_steps = ["Analyze problem requirements", "Retrieve related knowledge", "Organize and structure information", "Write initial answer", "Check and optimize answer", "Generate final response"]

#     # Adjust thinking steps based on prompt
#     if "code" in prompt or "programming" in prompt:
#         thinking_steps = ["Understand code requirements", "Design code structure", "Write core functions", "Implement error handling", "Test code functionality", "Optimize code efficiency"]

#     # Ensure step count is reasonable
#     actual_steps = min(steps, len(thinking_steps))

#     # Simulate thinking process
#     for i in range(actual_steps):
#         step_msg = thinking_steps[i]
#         if callback:
#             callback(step_msg)
#         await asyncio.sleep(delay * (0.5 + random.random()))

#     # Generate answer
#     result = f"This is my answer to the question「{prompt[:30]}...」.\n\n"
#     result += "Based on my analysis, here are some suggestions:\n"
#     result += "1. First, confirm the core of the question\n"
#     result += "2. Next, analyze possible solutions\n"
#     result += "3. Finally, select the most appropriate method to implement"

#     # Record output
#     monitor.record_communication("out", result)
#     return result

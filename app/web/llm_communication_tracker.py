# # Add LLM communication hooks at appropriate locations
# from app.web.thinking_tracker import ThinkingTracker
# from app.llm import LLM

# # Track LLM communication content using monkey patching.
# # This class provides a context manager interface for tracking LLM communications.
# # It wraps the LLM's completion method to capture both input and output.
# class LLMCommunicationTracker:
#     """Track LLM communication content using monkey patching.
    
#     This class provides a context manager interface for tracking LLM communications.
#     It wraps the LLM's completion method to capture both input and output.
    
#     Attributes:
#         session_id (str): Unique identifier for the tracking session
#         agent (Optional[Any]): The agent instance containing the LLM
#         original_completion (Optional[Callable]): Original completion method
#     """


#     def __init__(self, session_id: str, agent=None):
#         """Initialize the communication tracker.
        
#         Args:
#             session_id: Unique identifier for the tracking session
#             agent: Optional agent instance containing the LLM
#         """        
#         self.session_id = session_id
#         self.agent = agent
#         self.original_run_method = None

#         # If agent is provided, install hooks
#         if agent and hasattr(agent, "llm") and hasattr(agent.llm, "completion"):
#             self.install_hooks()

#     def install_hooks(self):
#         """Install hooks to capture LLM communication content"""
#         if not self.agent or not hasattr(self.agent, "llm"):
#             return False

#         # Save original method
#         llm = self.agent.llm
#         if hasattr(llm, "completion"):
#             self.original_completion = llm.completion
#             # Replace with our wrapped method
#             llm.completion = self._wrap_completion(self.original_completion)
#             return True
#         return False

#     def uninstall_hooks(self):
#         """Uninstall hooks, restore original method"""
#         if self.agent and hasattr(self.agent, "llm") and self.original_completion:
#             self.agent.llm.completion = self.original_completion

#     def _wrap_completion(self, original_method):
#         """Wrap LLM's completion method to capture input and output"""
#         session_id = self.session_id

#         async def wrapped_completion(*args, **kwargs):
#             # Record input
#             prompt = kwargs.get("prompt", "")
#             if not prompt and args:
#                 prompt = args[0]
#             if prompt:
#                 ThinkingTracker.add_communication(
#                     session_id,
#                     "Send to LLM",
#                     prompt[:500] + ("..." if len(prompt) > 500 else ""),
#                 )

#             # Call original method
#             result = await original_method(*args, **kwargs)

#             # Record output
#             if result:
#                 content = result
#                 if isinstance(result, dict) and "content" in result:
#                     content = result["content"]
#                 elif hasattr(result, "content"):
#                     content = result.content

#                 if isinstance(content, str):
#                     ThinkingTracker.add_communication(
#                         session_id,
#                         "Received from LLM",
#                         content[:500] + ("..." if len(content) > 500 else ""),
#                     )

#             return result

#         return wrapped_completion

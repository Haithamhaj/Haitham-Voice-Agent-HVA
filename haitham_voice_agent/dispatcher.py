"""
Dispatcher Module

Routes execution plan steps to appropriate tool modules.
Handles tool responses and error propagation.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional

from .config import Config

logger = logging.getLogger(__name__)


class ToolDispatcher:
    """Dispatcher for routing tool calls"""
    
    def __init__(self):
        self.tools = {}
        logger.info("Tool Dispatcher initialized")
        self._register_default_tools()
        
    def _register_default_tools(self):
        """Register default system tools"""
        from haitham_voice_agent.tools.memory.voice_tools import VoiceMemoryTools
        from haitham_voice_agent.tools.gmail.connection_manager import ConnectionManager
        from haitham_voice_agent.tools.files import FileTools
        from haitham_voice_agent.tools.tasks.task_manager import task_manager
        from haitham_voice_agent.tools.system_tools import SystemTools
        from haitham_voice_agent.tools.browser import BrowserTools
        from haitham_voice_agent.tools.terminal import TerminalTools
        
        # Initialize tools
        # Note: Some might need async init, but for now we register the instances
        # The dispatch method handles async execution
        
        self.register_tool("memory", VoiceMemoryTools())
        self.register_tool("gmail", ConnectionManager())
        self.register_tool("files", FileTools())
        self.register_tool("tasks", task_manager) # TaskManager is already instantiated
        self.register_tool("system", SystemTools())
        self.register_tool("browser", BrowserTools())
        self.register_tool("terminal", TerminalTools())
    
    def register_tool(self, name: str, handler):
        """
        Register a tool handler
        
        Args:
            name: Tool name (e.g., 'files', 'gmail', 'memory')
            handler: Tool handler object with execute method
        """
        self.tools[name] = handler
        logger.info(f"Registered tool: {name}")
    
    async def dispatch(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """
        Dispatch a single execution step to the appropriate tool
        
        Args:
            step: Step dictionary with {tool, action, params}
            
        Returns:
            dict: Tool execution result
        """
        tool_name = step.get("tool")
        action = step.get("action")
        params = step.get("params", {})
        
        logger.info(f"Dispatching: {tool_name}.{action}({params})")
        
        # Check if tool is registered
        if tool_name not in self.tools:
            error_msg = f"Tool not found: {tool_name}"
            logger.error(error_msg)
            return {
                "error": True,
                "error_type": "ToolNotFoundError",
                "message": error_msg,
                "suggestion": f"Available tools: {', '.join(self.tools.keys())}"
            }
        
        # Get tool handler
        handler = self.tools[tool_name]
        
        # Check if action exists
        if not hasattr(handler, action):
            error_msg = f"Action not found: {tool_name}.{action}"
            logger.error(error_msg)
            return {
                "error": True,
                "error_type": "ActionNotFoundError",
                "message": error_msg,
                "suggestion": f"Check available actions for {tool_name}"
            }
        
        # Execute action
        try:
            action_method = getattr(handler, action)
            result = await action_method(**params)
            
            logger.info(f"Tool execution successful: {tool_name}.{action}")
            return result
            
        except Exception as e:
            logger.error(f"Tool execution failed: {e}", exc_info=True)
            return {
                "error": True,
                "error_type": type(e).__name__,
                "message": str(e),
                "suggestion": "Check tool parameters and try again"
            }
    
    async def execute_plan(self, plan: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Execute a complete execution plan
        
        Args:
            plan: Execution plan with steps array
            
        Returns:
            list: Results from each step
        """
        steps = plan.get("steps", [])
        logger.info(f"Executing plan with {len(steps)} steps")
        
        results = []
        
        for i, step in enumerate(steps):
            logger.info(f"Executing step {i+1}/{len(steps)}")
            
            # Handle variable substitution from previous steps
            # e.g., "$step1.id" -> results[0]["id"]
            step = self._substitute_variables(step, results)
            
            # Execute step
            result = await self.dispatch(step)
            results.append(result)
            
            # Stop execution if error occurred
            if result.get("error", False):
                logger.error(f"Step {i+1} failed, stopping execution")
                break
        
        return results
    
    def _substitute_variables(self, step: Dict[str, Any], previous_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Substitute variables in step parameters with values from previous results
        
        Args:
            step: Step dictionary
            previous_results: Results from previous steps
            
        Returns:
            dict: Step with substituted variables
        """
        params = step.get("params", {})
        substituted_params = {}
        
        for key, value in params.items():
            if isinstance(value, str) and value.startswith("$step"):
                # Parse variable reference: $step1.id -> step_index=0, field="id"
                try:
                    parts = value[1:].split(".")  # Remove $ and split
                    step_ref = parts[0]  # e.g., "step1"
                    field = parts[1] if len(parts) > 1 else None
                    
                    # Extract step index
                    step_index = int(step_ref.replace("step", "")) - 1
                    
                    # Get value from previous result
                    if 0 <= step_index < len(previous_results):
                        result = previous_results[step_index]
                        
                        if field:
                            if isinstance(result, dict):
                                substituted_value = result.get(field)
                            else:
                                # If result is not a dict, we can't get a field from it
                                logger.warning(f"Cannot get field '{field}' from non-dict result: {result}")
                                substituted_value = None
                        else:
                            substituted_value = result
                        
                        if substituted_value is not None:
                            substituted_params[key] = substituted_value
                            logger.debug(f"Substituted {value} -> {substituted_value}")
                        else:
                            substituted_params[key] = value
                    else:
                        logger.warning(f"Invalid step reference: {value}")
                        substituted_params[key] = value
                        
                except Exception as e:
                    logger.warning(f"Failed to substitute variable {value}: {e}")
                    substituted_params[key] = value
            else:
                substituted_params[key] = value
        
        step["params"] = substituted_params
        return step


# Singleton instance
_dispatcher_instance: Optional[ToolDispatcher] = None


def get_dispatcher() -> ToolDispatcher:
    """Get singleton dispatcher instance"""
    global _dispatcher_instance
    if _dispatcher_instance is None:
        _dispatcher_instance = ToolDispatcher()
    return _dispatcher_instance



def dispatch_action(plan: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute an execution plan synchronously
    
    Args:
        plan: Execution plan dictionary
        
    Returns:
        dict: Execution result
    """
    dispatcher = get_dispatcher()
    
    # Run async execution in a new event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        results = loop.run_until_complete(dispatcher.execute_plan(plan))
        
        # Aggregate results
        if not results:
            return {"success": False, "message": "No steps executed"}
            
        # Return the last result as the primary result
        # Ideally we should aggregate, but for now last result is fine
        last_result = results[-1]
        
        # Ensure success flag exists
        if "success" not in last_result:
            last_result["success"] = not last_result.get("error", False)
            
        return last_result
        
    except Exception as e:
        logger.error(f"Dispatch failed: {e}")
        return {"success": False, "message": str(e)}
    finally:
        loop.close()


if __name__ == "__main__":
    # Test dispatcher
    async def test():
        dispatcher = get_dispatcher()
        
        print("Testing Tool Dispatcher...")
        
        # Create a mock tool
        class MockTool:
            async def test_action(self, param1, param2="default"):
                return {"result": f"Executed with {param1}, {param2}"}
        
        # Register mock tool
        dispatcher.register_tool("mock", MockTool())
        
        # Test single dispatch
        print("\nTesting single dispatch:")
        step = {
            "tool": "mock",
            "action": "test_action",
            "params": {"param1": "value1", "param2": "value2"}
        }
        result = await dispatcher.dispatch(step)
        print(f"Result: {result}")
        
        # Test plan execution
        print("\nTesting plan execution:")
        plan = {
            "steps": [
                {"tool": "mock", "action": "test_action", "params": {"param1": "step1"}},
                {"tool": "mock", "action": "test_action", "params": {"param1": "step2"}}
            ]
        }
        results = await dispatcher.execute_plan(plan)
        print(f"Results: {results}")
        
        print("\nDispatcher test completed")
    
    asyncio.run(test())

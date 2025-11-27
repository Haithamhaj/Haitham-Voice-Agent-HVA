"""
Terminal Tools (Safe Mode)

Safe terminal command execution for HVA.
Implements operations from Master SRS Section 3.7.
"""

import subprocess
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class TerminalTools:
    """Safe terminal operations"""
    
    # Whitelist of allowed commands (from Master SRS)
    ALLOWED_COMMANDS = {
        'ls', 'pwd', 'echo', 'whoami', 'df'
    }
    
    def __init__(self):
        logger.info("TerminalTools initialized (safe mode)")
    
    async def execute_command(self, command: str) -> Dict[str, Any]:
        """
        Execute a safe terminal command
        
        Args:
            command: Command to execute
            
        Returns:
            dict: Command output
        """
        try:
            # Parse command
            parts = command.strip().split()
            
            if not parts:
                return {
                    "error": True,
                    "message": "Empty command"
                }
            
            cmd_name = parts[0]
            
            # Check if command is allowed
            if cmd_name not in self.ALLOWED_COMMANDS:
                logger.warning(f"Blocked unsafe command: {cmd_name}")
                return {
                    "error": True,
                    "message": f"Command not allowed: {cmd_name}",
                    "suggestion": f"Allowed commands: {', '.join(self.ALLOWED_COMMANDS)}"
                }
            
            # Check for dangerous patterns
            if 'sudo' in command or '&&' in command or '|' in command or ';' in command:
                logger.warning(f"Blocked command with dangerous pattern: {command}")
                return {
                    "error": True,
                    "message": "Command contains dangerous patterns (sudo, pipes, chaining)",
                    "suggestion": "Only simple, safe commands are allowed"
                }
            
            # Execute command
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=5  # 5 second timeout
            )
            
            logger.info(f"Executed safe command: {command}")
            
            return {
                "command": command,
                "output": result.stdout,
                "error_output": result.stderr if result.stderr else None,
                "return_code": result.returncode,
                "success": result.returncode == 0
            }
            
        except subprocess.TimeoutExpired:
            logger.error(f"Command timed out: {command}")
            return {
                "error": True,
                "message": "Command timed out (5 second limit)"
            }
        except Exception as e:
            logger.error(f"Command execution failed: {e}")
            return {
                "error": True,
                "message": str(e)
            }
    
    async def list_allowed_commands(self) -> Dict[str, Any]:
        """
        Get list of allowed commands
        
        Returns:
            dict: Allowed commands with descriptions
        """
        commands_info = {
            "ls": "List directory contents",
            "pwd": "Print working directory",
            "echo": "Display a line of text",
            "whoami": "Print current user name",
            "df": "Display disk space usage"
        }
        
        return {
            "allowed_commands": list(self.ALLOWED_COMMANDS),
            "descriptions": commands_info,
            "count": len(self.ALLOWED_COMMANDS)
        }


if __name__ == "__main__":
    # Test terminal tools
    import asyncio
    
    async def test():
        tools = TerminalTools()
        
        print("Testing TerminalTools...")
        
        # Test allowed commands
        print("\nAllowed commands:")
        result = await tools.list_allowed_commands()
        for cmd, desc in result["descriptions"].items():
            print(f"  {cmd}: {desc}")
        
        # Test safe command
        print("\nExecuting 'pwd':")
        result = await tools.execute_command("pwd")
        print(f"Output: {result.get('output', '').strip()}")
        
        # Test safe command
        print("\nExecuting 'whoami':")
        result = await tools.execute_command("whoami")
        print(f"Output: {result.get('output', '').strip()}")
        
        # Test blocked command
        print("\nTrying blocked command 'rm':")
        result = await tools.execute_command("rm test.txt")
        print(f"Result: {result.get('message')}")
        
        # Test dangerous pattern
        print("\nTrying dangerous pattern 'ls && rm':")
        result = await tools.execute_command("ls && rm test.txt")
        print(f"Result: {result.get('message')}")
        
        print("\nTerminalTools test completed")
    
    asyncio.run(test())

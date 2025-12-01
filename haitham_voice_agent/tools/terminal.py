"""
Terminal Tools (Traffic Light Security Model)

Safe terminal command execution for HVA.
Implements "Traffic Light" security logic:
- GREEN: Safe, read-only commands (Execute immediately)
- YELLOW: Restricted/Side-effects (Require Confirmation)
- RED: Blocked/System Critical (Deny)
"""

import subprocess
import logging
import shlex
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class TerminalTools:
    """
    Safe terminal operations with Traffic Light Security.
    """
    
    # 🟢 GREEN: Safe, Read-Only, Informational
    GREEN_LIST = {
        'ls', 'pwd', 'echo', 'cat', 'grep', 'find', 'whoami', 'df', 
        'git status', 'git log', 'git diff', 'date', 'uptime', 'hostname'
    }

    # 🔴 RED: Blocked, Dangerous, System Critical
    RED_LIST = {
        'mkfs', 'dd', 'shutdown', 'reboot', 'visudo', 'su', 'sudo', 
        'chmod', 'chown', 'rm -rf /', ':(){ :|:& };:'
    }
    
    # 🟡 YELLOW: Everything else (Requires Confirmation)
    # Examples: python3, pip, npm, docker, ffmpeg, rm, mv, code, mkdir, git commit
    
    def __init__(self):
        logger.info("TerminalTools initialized (Traffic Light Security)")
    
    def _classify_command(self, command_name: str) -> str:
        """Classify command as GREEN, YELLOW, or RED"""
        if command_name in self.GREEN_LIST:
            return "GREEN"
        if command_name in self.RED_LIST:
            return "RED"
        return "YELLOW"

    async def execute_command(self, command: str, confirmed: bool = False) -> Dict[str, Any]:
        """
        Execute a terminal command with security checks.
        
        Args:
            command: Command string to execute
            confirmed: Whether the user has explicitly confirmed execution (for YELLOW commands)
            
        Returns:
            dict: Execution result or confirmation request
        """
        try:
            # 1. Basic Validation
            if not command or not command.strip():
                return {"error": True, "message": "Empty command"}
            
            # 2. Block Chaining & Injection (Strict)
            dangerous_chars = [';', '&&', '|', '`', '$(']
            if any(char in command for char in dangerous_chars):
                logger.warning(f"Blocked chained command: {command}")
                return {
                    "error": True,
                    "message": "Command chaining (;, &&, |) is NOT allowed. Please execute steps sequentially.",
                    "security_alert": "Injection Attempt Blocked"
                }

            # 3. Parse Command safely
            try:
                parts = shlex.split(command)
            except ValueError as e:
                return {"error": True, "message": f"Invalid command syntax: {e}"}
                
            if not parts:
                return {"error": True, "message": "Empty command parsed"}
                
            cmd_name = parts[0]
            
            # 4. Traffic Light Classification
            security_level = self._classify_command(cmd_name)
            
            # 🔴 RED: Block immediately
            if security_level == "RED":
                logger.warning(f"Blocked RED command: {cmd_name}")
                return {
                    "error": True,
                    "message": f"Command '{cmd_name}' is BLOCKED by security policy.",
                    "security_alert": "Critical Command Blocked"
                }
                
            # 🟡 YELLOW: Require Confirmation
            if security_level == "YELLOW" and not confirmed:
                logger.info(f"Paused YELLOW command for confirmation: {cmd_name}")
                return {
                    "status": "confirmation_required",
                    "message": f"Command '{cmd_name}' requires confirmation.",
                    "command": command,
                    "risk_level": "medium",
                    "suggestion": "Please confirm if you want to execute this command."
                }

            # 🟢 GREEN or Confirmed YELLOW: Execute
            logger.info(f"Executing {security_level} command: {command}")
            
            # Execute without shell=True for security
            result = subprocess.run(
                parts,
                capture_output=True,
                text=True,
                timeout=30  # 30s timeout for safety
            )
            
            return {
                "success": result.returncode == 0,
                "command": command,
                "output": result.stdout,
                "error_output": result.stderr if result.stderr else None,
                "return_code": result.returncode
            }
            
        except subprocess.TimeoutExpired:
            return {"error": True, "message": "Command timed out (30s limit)"}
        except FileNotFoundError:
            return {"error": True, "message": f"Command not found: {parts[0]}"}
        except Exception as e:
            logger.error(f"Command execution failed: {e}")
            return {"error": True, "message": str(e)}

    async def list_allowed_commands(self) -> Dict[str, Any]:
        """Return list of safe (GREEN) commands"""
        return {
            "green_commands": list(self.GREEN_LIST),
            "policy": "Green commands execute immediately. Others require confirmation. Chaining is blocked."
        }

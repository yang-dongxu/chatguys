from typing import Callable, Dict, Optional, Any
from .context_manager import ContextManager
from .agent_manager import AgentManager


class CommandProcessor:
    def __init__(self, context_manager: ContextManager, agent_manager: AgentManager):
        """Initialize the CommandProcessor.
        
        Args:
            context_manager (ContextManager): The conversation context manager
            agent_manager (AgentManager): The agent configuration manager
        """
        self.context_manager = context_manager
        self.agent_manager = agent_manager
        self.commands: Dict[str, Callable] = {
            '/help': self.cmd_help,
            '/reset': self.cmd_reset,
            '/reload': self.cmd_reload,
            '/roles': self.cmd_roles,
        }
    
    def is_command(self, message: str) -> bool:
        """Check if a message is a system command.
        
        Args:
            message (str): The message to check
            
        Returns:
            bool: True if the message is a command, False otherwise
        """
        return message.startswith('/')
    
    def process_command(self, command: str) -> str:
        """Process a system command and return the response.
        
        Args:
            command (str): The command to process
            
        Returns:
            str: The command response
        """
        # Split command and arguments
        parts = command.split()
        cmd = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        if cmd in self.commands:
            return self.commands[cmd](*args)
        else:
            return f"Unknown command: {cmd}. Type /help for available commands."
    
    def cmd_help(self, *args) -> str:
        """Show help information.
        
        Returns:
            str: Help message
        """
        return """Available commands:
/help - Show this help message
/reset - Clear conversation history
/reload - Reload agent configurations
/roles - List available roles

To send a message to a specific agent, use @RoleName at the start of your message.
Example: @Tech How do I implement a binary search?"""
    
    def cmd_reset(self, *args) -> str:
        """Reset the conversation history.
        
        Returns:
            str: Confirmation message
        """
        self.context_manager.clear_history()
        return "Conversation history has been cleared."
    
    def cmd_reload(self, *args) -> str:
        """Reload agent configurations.
        
        Returns:
            str: Confirmation message
        """
        try:
            self.agent_manager.load_configurations()
            return "Agent configurations have been reloaded."
        except Exception as e:
            return f"Error reloading configurations: {str(e)}"
    
    def cmd_roles(self, *args) -> str:
        """List available roles.
        
        Returns:
            str: List of available roles
        """
        roles = self.agent_manager.list_roles()
        if not roles:
            return "No roles are currently configured."
        
        return "Available roles:\n" + "\n".join(f"- {role}" for role in roles) 
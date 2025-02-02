"""Command processing for the chat application."""

from typing import Callable, Dict, Optional
from rich.markdown import Markdown

from ..core.context import ContextManager
from ..core.config import ConfigManager


class CommandProcessor:
    """Handles system commands and their execution."""
    
    def __init__(self, context_manager: ContextManager, config_manager: ConfigManager):
        """Initialize the CommandProcessor.
        
        Args:
            context_manager (ContextManager): The conversation context manager
            config_manager (ConfigManager): The configuration manager
        """
        self.context_manager = context_manager
        self.config_manager = config_manager
        self.commands: Dict[str, Callable] = {
            '/help': self.cmd_help,
            '/reset': self.cmd_reset,
            '/reload': self.cmd_reload,
            '/roles': self.cmd_roles,
            '/quit': self.cmd_quit,
            '/exit': self.cmd_quit,
        }
    
    def is_command(self, message: str) -> bool:
        """Check if a message is a system command.
        
        Args:
            message (str): The message to check
            
        Returns:
            bool: True if the message is a command, False otherwise
        """
        return message.strip().startswith('/')
    
    def process_command(self, command: str) -> str:
        """Process a system command and return the response.
        
        Args:
            command (str): The command to process
            
        Returns:
            str: The command response
        """
        # Split command and arguments
        parts = command.strip().split()
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
/quit or /exit - Exit the application

To send a message to a specific agent, use @RoleName at the start of your message.
Example: @Tech How do I implement a binary search?

You can also mention multiple agents in one message:
Example: @Tech @Default @Creative how would you describe the internet?"""
    
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
            self.config_manager.load_configurations()
            return "Agent configurations have been reloaded."
        except Exception as e:
            return f"Error reloading configurations: {str(e)}"
    
    def cmd_roles(self, *args) -> str:
        """List available roles.
        
        Returns:
            str: List of available roles
        """
        roles = self.config_manager.list_roles()
        if not roles:
            return "No roles are currently configured."
        
        role_descriptions = []
        for role in roles:
            config = self.config_manager.get_role_config(role)
            if config and 'prompt' in config:
                # Extract first sentence of prompt for brief description
                description = config['prompt'].split('.')[0].strip()
                role_descriptions.append(f"• **{role}**\n  {description}")
            else:
                role_descriptions.append(f"• **{role}**")
        
        return "Available roles:\n\n" + "\n\n".join(role_descriptions)
    
    def cmd_quit(self, *args) -> str:
        """Handle quit command.
        
        Returns:
            str: Goodbye message
        """
        return "Goodbye!" 
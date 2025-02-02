"""Input handling for the chat application."""

from prompt_toolkit import PromptSession
from prompt_toolkit.formatted_text import HTML
from rich.console import Console

from ..utils.completion import create_combined_completer
from ..core.config import ConfigManager
from ..cli.commands import CommandProcessor


class InputHandler:
    """Handles user input with completion support."""
    
    def __init__(self, config_manager: ConfigManager, command_processor: CommandProcessor):
        """Initialize the InputHandler.
        
        Args:
            config_manager (ConfigManager): The configuration manager
            command_processor (CommandProcessor): The command processor
        """
        self.config_manager = config_manager
        self.command_processor = command_processor
        self.session = PromptSession()
        self.console = Console()
    
    def _get_completer(self):
        """Get the combined completer for roles and commands.
        
        Returns:
            WordCompleter: Combined completer
        """
        roles = self.config_manager.list_roles()
        commands = list(self.command_processor.commands.keys())
        return create_combined_completer(roles, commands)
    
    async def get_input(self) -> str:
        """Get user input with completion support.
        
        Returns:
            str: User input
        """
        # Create a completer that handles both @ and / patterns
        completer = self._get_completer()
        
        # Get input with completion
        result = await self.session.prompt_async(
            HTML("\n<b>You:</b> "),
            completer=completer,
            complete_while_typing=True
        )
        
        return result.strip()
    
    def display_error(self, message: str) -> None:
        """Display an error message.
        
        Args:
            message (str): Error message to display
        """
        self.console.print(f"[red]Error:[/red] {message}")
    
    def display_message(self, message: str) -> None:
        """Display a message.
        
        Args:
            message (str): Message to display
        """
        self.console.print(message) 
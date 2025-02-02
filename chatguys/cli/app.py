"""Main chat application."""

import os
import signal
import asyncio
from typing import List, Tuple
from rich.console import Console
from rich.markdown import Markdown
from dotenv import load_dotenv

from ..core.agent import Agent
from ..core.config import ConfigManager
from ..core.context import ContextManager
from ..cli.commands import CommandProcessor
from ..cli.input import InputHandler
from ..utils.text import extract_mentions, format_role_message


class ChatApp:
    """Main chat application class."""
    
    def __init__(self):
        """Initialize the chat application."""
        # Load environment variables
        load_dotenv()
        
        # Store default OpenAI settings
        self.default_api_key = os.getenv("OPENAI_API_KEY")
        self.default_base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        
        if not self.default_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        
        # Initialize core components
        self.config_manager = ConfigManager()
        self.context_manager = ContextManager()
        
        # Initialize CLI components
        self.command_processor = CommandProcessor(
            self.context_manager,
            self.config_manager
        )
        self.input_handler = InputHandler(
            self.config_manager,
            self.command_processor
        )
        
        # Flag for graceful shutdown
        self.should_exit = False
    
    def _handle_signal(self, signum, frame):
        """Handle system signals for graceful shutdown."""
        self.input_handler.display_message(
            "\nReceived shutdown signal. Use 'exit' or 'quit' to exit properly."
        )
        self.should_exit = True
    
    async def _process_agent_response(
        self, role_name: str, message: str
    ) -> Tuple[str, str]:
        """Process a single agent's response.
        
        Args:
            role_name (str): Name of the role to use
            message (str): Message for this role
            
        Returns:
            Tuple[str, str]: (role_name, response)
        """
        # Get role configuration
        role_config = self.config_manager.get_role_config(role_name)
        if not role_config:
            return role_name, f"Error: Role '{role_name}' not found."
        
        # Create agent instance
        agent = Agent(
            role_name,
            role_config,
            self.default_api_key,
            self.default_base_url
        )
        
        # Get response
        response = await agent.get_response(
            message,
            self.context_manager.get_history()
        )
        
        # Add response to history
        self.context_manager.add_message(role_name, response)
        
        return role_name, response
    
    async def run(self):
        """Run the chat application."""
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGTERM, self._handle_signal)
        
        self.input_handler.display_message(Markdown("# Welcome to ChatGuys!"))
        self.input_handler.display_message("Type /help for available commands.")
        
        while not self.should_exit:
            try:
                # Get user input
                message = await self.input_handler.get_input()
                
                # Skip empty messages
                if not message.strip():
                    continue
                
                # Handle exit command
                if message.lower() in ['exit', 'quit', '/quit', '/exit']:
                    self.input_handler.display_message("Goodbye!")
                    break
                
                # Process the message
                if self.command_processor.is_command(message):
                    # Handle system command
                    response = self.command_processor.process_command(message)
                    self.input_handler.display_message(Markdown(response))
                else:
                    # Extract all roles and their messages
                    roles_and_messages = extract_mentions(message)
                    
                    # Skip if no valid messages
                    if not roles_and_messages:
                        continue
                    
                    # Add user message to history
                    for role_name, clean_message in roles_and_messages:
                        context_message = format_role_message(role_name, clean_message)
                        self.context_manager.add_message("user", context_message)
                    
                    try:
                        # Create coroutines for each role's response
                        coroutines = [
                            self._process_agent_response(role_name, clean_message)
                            for role_name, clean_message in roles_and_messages
                        ]
                        
                        # Wait for all responses
                        responses = await asyncio.gather(*coroutines)
                        
                        # Display responses in original order
                        for role_name, response in responses:
                            self.input_handler.display_message(
                                f"\n[bold]{role_name}[/bold]:"
                            )
                            self.input_handler.display_message(Markdown(response))
                    
                    except Exception as e:
                        self.input_handler.display_error(f"Error getting responses: {str(e)}")
            
            except asyncio.CancelledError:
                # Handle cancellation gracefully
                self.input_handler.display_message("\nShutting down gracefully...")
                break
            except KeyboardInterrupt:
                # Handle Ctrl+C gracefully
                self.input_handler.display_message(
                    "\nUse 'exit' or 'quit' to exit the application."
                )
            except Exception as e:
                self.input_handler.display_error(str(e)) 
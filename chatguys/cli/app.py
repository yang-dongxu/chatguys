"""Main chat application."""

import os
import signal
import asyncio
from pathlib import Path
from typing import List, Tuple
from rich.console import Console
from rich.markdown import Markdown
from rich.status import Status
from dotenv import load_dotenv

from ..core.agent import Agent
from ..core.config import ConfigManager
from ..core.context import ContextManager
from ..cli.commands import CommandProcessor
from ..cli.input import InputHandler
from ..utils.text import extract_mentions, format_role_message


class ChatApp:
    """Main chat application class."""
    
    def __init__(self, session_name: str = None, load_session: str = None):
        """Initialize the chat application.
        
        Args:
            session_name (str, optional): Custom name for the chat session files
            load_session (str, optional): Name of a previous session to load
        """
        # Get config directory
        self.config_dir = Path.home() / ".config" / "chatguys"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Load environment variables from config directory
        env_file = self.config_dir / ".env"
        if not env_file.exists():
            raise ValueError(f"API keys not configured. Please edit {env_file}")
        print(f"Loading environment variables from {env_file}")
        load_dotenv(env_file, override=True)
        
        # Store default OpenAI settings
        self.default_api_key = os.getenv("OPENAI_API_KEY")
        self.default_base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        
        if not self.default_api_key:
            raise ValueError(f"OPENAI_API_KEY not set in {env_file}")
        
        # Initialize core components
        self.config_manager = ConfigManager()
        
        # Initialize context manager with session name
        session_name_to_use = load_session or session_name
        self.context_manager = ContextManager(session_name=session_name_to_use)
        
        # Try to load previous session if requested
        if load_session:
            if not self.context_manager.load_history(load_session):
                print(f"Warning: Could not load session '{load_session}'")
        elif session_name:
            # Create new session with custom name
            self.context_manager.load_history(session_name)
        
        # Initialize CLI components
        self.command_processor = CommandProcessor(
            self.context_manager,
            self.config_manager
        )
        self.input_handler = InputHandler(
            self.config_manager,
            self.command_processor
        )
        
        # Flag for graceful shutdown and response cancellation
        self.should_exit = False
        self.current_task = None
    
    def _handle_signal(self, signum, frame):
        """Handle system signals for graceful shutdown."""
        if self.current_task and not self.current_task.done():
            # Cancel current response task
            self.current_task.cancel()
        else:
            self.input_handler.display_message(
                "\nReceived shutdown signal. Use 'exit' or 'quit' to exit properly."
            )
            self.should_exit = True
    
    async def _process_agent_response(
        self, role_name: str, message: str, status: Status
    ) -> Tuple[str, str]:
        """Process a single agent's response.
        
        Args:
            role_name (str): Name of the role to use
            message (str): Message for this role
            status (Status): Status indicator to update
            
        Returns:
            Tuple[str, str]: (role_name, response)
        """
        try:
            # Get role configuration
            status.update(f"[bold blue]{role_name}[/]: Loading role configuration...")
            role_config = self.config_manager.get_role_config(role_name)
            if not role_config:
                return role_name, f"Error: Role '{role_name}' not found."
            
            # Create agent instance
            status.update(f"[bold blue]{role_name}[/]: Initializing agent...")
            agent = Agent(
                role_name,
                role_config,
                self.default_api_key,
                self.default_base_url
            )
            
            # Update status for context preparation
            status.update(f"[bold blue]{role_name}[/]: Preparing context ({len(self.context_manager.get_history())} messages)...")
            
            # Get response
            status.update(f"[bold blue]{role_name}[/]: Waiting for API response...")
            response = await agent.get_response(
                message,
                self.context_manager.get_history()
            )
            
            # Add response to history
            status.update(f"[bold blue]{role_name}[/]: Saving response...")
            self.context_manager.add_message(role_name, response)
            
            return role_name, response
        except asyncio.CancelledError:
            status.update(f"[bold red]{role_name}[/]: Cancelling...")
            raise
        except Exception as e:
            error_msg = f"Error from {role_name}: {str(e)}"
            self.context_manager.add_message("system", error_msg)
            return role_name, error_msg
    
    async def run(self):
        """Run the chat application."""
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGTERM, self._handle_signal)
        
        # Display welcome message
        self.input_handler.display_message(Markdown("# Welcome to ChatGuys!"))
        
        # Show session info
        session_name = self.context_manager.session_file.stem
        self.input_handler.display_message(
            f"\nCurrent session: [bold blue]{session_name}[/]"
        )
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
                    quit_message = self.command_processor.cmd_quit()
                    self.input_handler.display_message(quit_message)
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
                        # Create status indicator
                        with Status("Starting response generation...", spinner="dots") as status:
                            # Create tasks for each role's response
                            tasks = [
                                asyncio.create_task(
                                    self._process_agent_response(role_name, clean_message, status)
                                )
                                for role_name, clean_message in roles_and_messages
                            ]
                            
                            # Store the gathering task for cancellation
                            self.current_task = asyncio.gather(*tasks)
                            
                            try:
                                # Wait for all responses
                                responses = await self.current_task
                                
                                # Display responses in original order
                                for role_name, response in responses:
                                    self.input_handler.display_message(
                                        f"\n[bold]{role_name}[/bold]:"
                                    )
                                    self.input_handler.display_message(Markdown(response))
                            except asyncio.CancelledError:
                                # Response was cancelled by Ctrl+C
                                self.input_handler.display_message("\n[bold red]Cancelling responses...[/]")
                                
                                # Cancel all tasks and wait for them to finish
                                for task in tasks:
                                    if not task.done():
                                        task.cancel()
                                
                                # Wait for all tasks to complete cancellation
                                try:
                                    await asyncio.wait(tasks, timeout=5.0)
                                except asyncio.TimeoutError:
                                    self.input_handler.display_message("[red]Force cancelling tasks...[/]")
                                
                                # Add cancellation to history
                                self.context_manager.add_message(
                                    "system",
                                    "Response generation was cancelled by user"
                                )
                                self.input_handler.display_message("\n[green]Cancelled successfully.[/]")
                            finally:
                                self.current_task = None
                                
                                # Clean up any remaining tasks
                                for task in tasks:
                                    if not task.done():
                                        task.cancel()
                    
                    except Exception as e:
                        error_msg = f"Error getting responses: {str(e)}"
                        self.input_handler.display_error(error_msg)
                        self.context_manager.add_message("system", error_msg)
            
            except asyncio.CancelledError:
                # Handle cancellation gracefully
                if self.current_task and not self.current_task.done():
                    self.current_task.cancel()
                    self.input_handler.display_message("\n[bold red]Cancelling...[/]")
                    try:
                        await asyncio.wait_for(self.current_task, timeout=5.0)
                    except (asyncio.TimeoutError, asyncio.CancelledError):
                        pass
                quit_message = self.command_processor.cmd_quit()
                self.input_handler.display_message(f"\n{quit_message}")
                break
            except KeyboardInterrupt:
                # Handle Ctrl+C gracefully
                if self.current_task and not self.current_task.done():
                    self.current_task.cancel()
                    self.input_handler.display_message("\n[bold red]Cancelling response...[/]")
                    try:
                        await asyncio.wait_for(self.current_task, timeout=5.0)
                        self.input_handler.display_message("[green]Cancelled successfully.[/]")
                    except (asyncio.TimeoutError, asyncio.CancelledError):
                        self.input_handler.display_message("[red]Force cancelled.[/]")
                else:
                    self.input_handler.display_message(
                        "\nUse 'exit' or 'quit' to exit the application."
                    )
            except Exception as e:
                error_msg = str(e)
                self.input_handler.display_error(error_msg)
                self.context_manager.add_message("system", error_msg) 
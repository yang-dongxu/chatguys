import os
import re
import asyncio
import signal
from typing import Optional, Tuple, List
import openai
from rich.console import Console
from rich.markdown import Markdown
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.formatted_text import HTML
from dotenv import load_dotenv

from .agent_manager import AgentManager
from .context_manager import ContextManager
from .command_processor import CommandProcessor


class ChatApp:
    def __init__(self):
        """Initialize the chat application."""
        # Load environment variables
        load_dotenv()
        
        # Store default OpenAI settings
        self.default_api_key = os.getenv("OPENAI_API_KEY")
        self.default_base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        
        if not self.default_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        
        # Initialize components
        self.agent_manager = AgentManager()
        self.context_manager = ContextManager()
        self.command_processor = CommandProcessor(
            self.context_manager, self.agent_manager
        )
        
        # Initialize rich console and prompt session
        self.console = Console()
        self.session = PromptSession()
        
        # Flag for graceful shutdown
        self.should_exit = False
    
    def _get_role_completer(self) -> WordCompleter:
        """Create a completer for role names.
        
        Returns:
            WordCompleter: Completer for role names
        """
        roles = self.agent_manager.list_roles()
        # Create completions for both "@Role" and just "Role"
        completions = [f"@{role}" for role in roles] + roles
        return WordCompleter(completions, ignore_case=True)
    
    def _get_command_completer(self) -> WordCompleter:
        """Create a completer for commands.
        
        Returns:
            WordCompleter: Completer for commands
        """
        # Get all available commands from the command processor
        commands = list(self.command_processor.commands.keys())
        return WordCompleter(commands, ignore_case=True)
    
    def _get_combined_completer(self) -> WordCompleter:
        """Create a completer that handles both roles and commands.
        
        Returns:
            WordCompleter: Combined completer for roles and commands
        """
        roles = self.agent_manager.list_roles()
        commands = list(self.command_processor.commands.keys())
        
        completions = (
            [f"@{role}" for role in roles] +  # @Role format
            roles +                           # Plain role names
            commands                         # Commands with /
        )
        
        return WordCompleter(
            completions,
            ignore_case=True,
            pattern=re.compile(r'^(@\w*|/\w*)$')  # Trigger on @ or /
        )
    
    async def _get_user_input(self) -> str:
        """Get user input with role and command completion support.
        
        Returns:
            str: User input
        """
        # Create a completer that handles both @ and / patterns
        completer = self._get_combined_completer()
        
        # Get input with completion
        result = await self.session.prompt_async(
            HTML("\n<b>You:</b> "),
            completer=completer,
            complete_while_typing=True
        )
        
        return result.strip()
    
    def _handle_signal(self, signum, frame):
        """Handle system signals for graceful shutdown."""
        self.console.print("\nReceived shutdown signal. Use 'exit' or 'quit' to exit properly.")
        self.should_exit = True
    
    def extract_roles(self, message: str) -> List[Tuple[str, str]]:
        """Extract all roles and their respective clean messages from user input.
        
        Args:
            message (str): Raw user input
            
        Returns:
            List[Tuple[str, str]]: List of (role_name, clean_message) pairs
        """
        message = message.strip()
        if not message:  # Handle empty input
            return []
            
        # Look for all @Role patterns in the message
        role_pattern = r'@(\w+)'
        matches = list(re.finditer(role_pattern, message))
        
        if not matches:
            # If no roles found and message is not empty, use Default
            return [("Default", message)] if message else []
        
        # Split message into segments based on role mentions
        segments = []
        last_end = 0
        
        for i, match in enumerate(matches):
            role_name = match.group(1)
            start, end = match.span()
            
            # If this is not the first role and there's text before it,
            # that text belongs to the previous role
            if i > 0 and start > last_end:
                segments.append((matches[i-1].group(1), message[last_end:start].strip()))
            
            # If this is the last role, add remaining text
            if i == len(matches) - 1 and end < len(message):
                segments.append((role_name, message[end:].strip()))
            # If this is not the last role, text until next role belongs to this one
            elif i < len(matches) - 1:
                next_start = matches[i+1].span()[0]
                if end < next_start:
                    segments.append((role_name, message[end:next_start].strip()))
            
            last_end = end
        
        # Filter out empty messages and ensure each role has content
        return [(role, msg) for role, msg in segments if msg.strip()]
    
    def _get_role_openai_settings(self, role_config: dict) -> Tuple[str, str]:
        """Get OpenAI settings for a specific role, falling back to defaults.
        
        Args:
            role_config (dict): Role configuration dictionary
            
        Returns:
            Tuple[str, str]: (api_key, base_url)
        """
        model_config = role_config.get('model', {})
        api_key = model_config.get('openai_api_key', self.default_api_key)
        base_url = model_config.get('openai_base_url', self.default_base_url)
        return api_key, base_url
    
    async def get_agent_response(self, role_name: str, message: str) -> str:
        """Get a response from an agent.
        
        Args:
            role_name (str): Name of the role to use
            message (str): User message
            
        Returns:
            str: Agent's response
        """
        role_config = self.agent_manager.get_role_config(role_name)
        if not role_config:
            return f"Error: Role '{role_name}' not found."
        
        # Get role-specific OpenAI settings
        api_key, base_url = self._get_role_openai_settings(role_config)
        
        # Create a client with role-specific settings
        client = openai.AsyncOpenAI(
            api_key=api_key,
            base_url=base_url
        )
        
        # Prepare the conversation history
        history = self.context_manager.get_history()
        
        # Convert history to OpenAI message format
        messages = [{"role": "system", "content": role_config['prompt']}]
        
        # Add a system message to explain the conversation format
        messages.append({
            "role": "system",
            "content": "The conversation history includes context about who messages are addressed to. "
                      "Pay attention to the conversation flow and context when responding."
        })
        
        for msg in history:
            if msg.role == "user":
                messages.append({"role": "user", "content": msg.content})
            else:
                # Just pass the content without additional role markers
                messages.append({"role": "assistant", "content": msg.content})
        
        # Add the current message
        messages.append({"role": "user", "content": message})
        
        try:
            # Call OpenAI API with role-specific client and full conversation history
            response = await client.chat.completions.create(
                model=role_config['model']['engine'],
                messages=messages,
                temperature=role_config['model']['temperature'],
                max_tokens=role_config['model']['max_tokens']
            )
            
            return response.choices[0].message.content
        except Exception as e:
            return f"Error getting response from {role_name}: {str(e)}"
    
    async def process_agent_response(self, role_name: str, message: str) -> Tuple[str, str]:
        """Process a single agent's response.
        
        Args:
            role_name (str): Name of the role to use
            message (str): Message for this role
            
        Returns:
            Tuple[str, str]: (role_name, response)
        """
        # Get and generate response
        response = await self.get_agent_response(role_name, message)
        
        # Add response to history
        self.context_manager.add_message(role_name, response)
        
        return role_name, response
    
    async def run(self):
        """Run the chat application."""
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGTERM, self._handle_signal)
        
        self.console.print(Markdown("# Welcome to ChatGuys!"))
        self.console.print("Type /help for available commands.")
        
        while not self.should_exit:
            try:
                # Get user input
                message = await self._get_user_input()
                
                # Skip empty messages
                if not message.strip():
                    continue
                
                # Handle exit command
                if message.lower() in ['exit', 'quit', '/quit', '/exit']:
                    self.console.print("Goodbye!")
                    break
                
                # Process the message
                if self.command_processor.is_command(message):
                    # Handle system command
                    response = self.command_processor.process_command(message)
                    self.console.print(Markdown(response))
                else:
                    # Extract all roles and their messages
                    roles_and_messages = self.extract_roles(message)
                    
                    # Skip if no valid messages
                    if not roles_and_messages:
                        continue
                    
                    # Add user message to history
                    for role_name, clean_message in roles_and_messages:
                        context_message = f"[To {role_name}] {clean_message}"
                        self.context_manager.add_message("user", context_message)
                    
                    try:
                        # Create coroutines for each role's response
                        coroutines = [
                            self.process_agent_response(role_name, clean_message)
                            for role_name, clean_message in roles_and_messages
                        ]
                        
                        # Wait for all responses
                        responses = await asyncio.gather(*coroutines)
                        
                        # Display responses in original order
                        for role_name, response in responses:
                            self.console.print(f"\n[bold]{role_name}[/bold]:")
                            self.console.print(Markdown(response))
                            # Ensure output is flushed
                            self.console.file.flush()
                    
                    except Exception as e:
                        self.console.print(f"[red]Error getting responses:[/red] {str(e)}")
            
            except asyncio.CancelledError:
                # Handle cancellation gracefully
                self.console.print("\nShutting down gracefully...")
                break
            except KeyboardInterrupt:
                # Handle Ctrl+C gracefully
                self.console.print("\nUse 'exit' or 'quit' to exit the application.")
            except Exception as e:
                self.console.print(f"[red]Error:[/red] {str(e)}")
                
        # Ensure final output is flushed
        self.console.file.flush()


def main():
    """Entry point for the chat application."""
    try:
        app = ChatApp()
        asyncio.run(app.run())
    except (KeyboardInterrupt, asyncio.CancelledError):
        # Handle exit signals gracefully at the top level
        Console().print("\nApplication shut down.")
    except Exception as e:
        Console().print(f"[red]Fatal error:[/red] {str(e)}")
        exit(1)


if __name__ == "__main__":
    main() 
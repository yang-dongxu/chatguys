"""Input completion utilities."""

import re
from typing import List
from prompt_toolkit.completion import WordCompleter


def create_role_completer(roles: List[str]) -> WordCompleter:
    """Create a completer for role names.
    
    Args:
        roles (List[str]): List of available role names
        
    Returns:
        WordCompleter: Completer for role names
    """
    # Create completions for both "@Role" and just "Role"
    completions = [f"@{role}" for role in roles] + roles
    return WordCompleter(completions, ignore_case=True)


def create_command_completer(commands: List[str]) -> WordCompleter:
    """Create a completer for commands.
    
    Args:
        commands (List[str]): List of available commands
        
    Returns:
        WordCompleter: Completer for commands
    """
    return WordCompleter(commands, ignore_case=True)


def create_combined_completer(roles: List[str], commands: List[str]) -> WordCompleter:
    """Create a completer that handles both roles and commands.
    
    Args:
        roles (List[str]): List of available role names
        commands (List[str]): List of available commands
        
    Returns:
        WordCompleter: Combined completer for roles and commands
    """
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
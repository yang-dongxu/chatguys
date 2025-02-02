"""Text processing utilities."""

import re
from typing import List, Tuple, Optional


def extract_mentions(message: str) -> List[Tuple[str, str]]:
    """Extract all role mentions and their associated messages from text.
    
    Args:
        message (str): Raw user input
        
    Returns:
        List[Tuple[str, str]]: List of (role_name, message) pairs
    """
    message = message.strip()
    if not message:
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


def format_role_message(role: str, message: str) -> str:
    """Format a message with role context.
    
    Args:
        role (str): Role name
        message (str): Message content
        
    Returns:
        str: Formatted message
    """
    return f"[To {role}] {message}" 
"""Text processing utilities."""

import re
from typing import List, Tuple, Optional


def extract_mentions(message: str) -> List[Tuple[str, str]]:
    """Extract all role mentions and their associated messages from text.
    
    Args:
        message (str): Raw user input
        
    Returns:
        List[Tuple[str, str]]: List of (role_name, message) pairs
        
    Examples:
        "@Tech @Creative tell me about AI" -> [("Tech", "tell me about AI"), ("Creative", "tell me about AI")]
        "tell me about AI @Tech @Creative" -> [("Tech", "tell me about AI"), ("Creative", "tell me about AI")]
        "@Tech explain code. @Creative write story about it" -> [("Tech", "explain code"), ("Creative", "write story about it")]
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
    
    # Check if mentions are tightly grouped (only whitespace between them)
    def are_mentions_grouped(matches_subset):
        if len(matches_subset) <= 1:
            return True
        for i in range(len(matches_subset) - 1):
            curr_end = matches_subset[i].span()[1]
            next_start = matches_subset[i + 1].span()[0]
            if not message[curr_end:next_start].isspace():
                return False
        return True
    
    # Check if all mentions are at the start
    first_match_start = matches[0].span()[0]
    prefix = message[:first_match_start].strip()
    start_mentions = []
    for match in matches:
        if match.span()[0] < len(prefix) + len(" ".join(m.group(0) for m in start_mentions)):
            start_mentions.append(match)
        else:
            break
    
    # Check if all mentions are at the end
    last_match_end = matches[-1].span()[1]
    suffix = message[last_match_end:].strip()
    end_mentions = []
    for match in reversed(matches):
        if match.span()[1] > len(message) - len(suffix) - len(" ".join(m.group(0) for m in end_mentions)):
            end_mentions.insert(0, match)
        else:
            break
    
    # Determine if this is a shared message case
    is_shared_message = (
        # All mentions at start
        (len(start_mentions) == len(matches) and not prefix) or
        # All mentions at end
        (len(end_mentions) == len(matches) and not suffix) or
        # All mentions are tightly grouped somewhere in the message
        are_mentions_grouped(matches)
    )
    
    if is_shared_message:
        # For mentions at start, use everything after
        if len(start_mentions) == len(matches):
            content = message[matches[-1].span()[1]:].strip()
        # For mentions at end, use everything before
        elif len(end_mentions) == len(matches):
            content = message[:matches[0].span()[0]].strip()
        # For grouped mentions in middle, split and use the longer content
        else:
            before = message[:matches[0].span()[0]].strip()
            after = message[matches[-1].span()[1]:].strip()
            content = after if len(after) > len(before) else before
            
        if not content:
            return []
        return [(match.group(1), content) for match in matches]
    else:
        # Role-specific messages case
        segments = []
        for i, match in enumerate(matches):
            role_name = match.group(1)
            start, end = match.span()
            
            # Get text until next mention or end of message
            if i < len(matches) - 1:
                next_start = matches[i + 1].span()[0]
                content = message[end:next_start].strip()
            else:
                content = message[end:].strip()
            
            if content:
                segments.append((role_name, content))
        
        return segments


def format_role_message(role: str, message: str) -> str:
    """Format a message with role context.
    
    Args:
        role (str): Role name
        message (str): Message content
        
    Returns:
        str: Formatted message
    """
    return f"[To {role}] {message}" 
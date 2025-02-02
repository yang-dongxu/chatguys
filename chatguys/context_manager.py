from typing import List, Dict, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Message:
    """Represents a single message in the conversation."""
    role: str  # The role/agent name or "user"
    content: str
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class ContextManager:
    def __init__(self, max_history: int = 100):
        """Initialize the ContextManager.
        
        Args:
            max_history (int): Maximum number of messages to keep in history
        """
        self.max_history = max_history
        self.history: List[Message] = []
    
    def add_message(self, role: str, content: str) -> None:
        """Add a new message to the conversation history.
        
        Args:
            role (str): The role/agent name or "user"
            content (str): The message content
        """
        message = Message(role=role, content=content)
        self.history.append(message)
        
        # Trim history if it exceeds max_history
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]
    
    def get_history(self, last_n: int = None) -> List[Message]:
        """Get the conversation history.
        
        Args:
            last_n (int, optional): Number of most recent messages to return
            
        Returns:
            List[Message]: List of messages
        """
        if last_n is None:
            return self.history
        return self.history[-last_n:]
    
    def clear_history(self) -> None:
        """Clear the conversation history."""
        self.history = []
    
    def format_for_prompt(self, last_n: int = None) -> str:
        """Format the conversation history for inclusion in a prompt.
        
        Args:
            last_n (int, optional): Number of most recent messages to include
            
        Returns:
            str: Formatted conversation history
        """
        history = self.get_history(last_n)
        formatted = []
        
        for msg in history:
            timestamp = msg.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            formatted.append(f"[{timestamp}] {msg.role}: {msg.content}")
        
        return "\n".join(formatted) 
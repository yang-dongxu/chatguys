"""Context management for chat history."""

from typing import List, Optional
from ..models.message import Message


class ContextManager:
    """Manages conversation history and context."""
    
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
    
    def get_history(self, last_n: Optional[int] = None) -> List[Message]:
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
    
    def format_history(self, last_n: Optional[int] = None) -> str:
        """Format the conversation history for display.
        
        Args:
            last_n (int, optional): Number of most recent messages to include
            
        Returns:
            str: Formatted conversation history
        """
        history = self.get_history(last_n)
        return "\n".join(msg.format_for_history() for msg in history) 
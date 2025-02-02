"""Message model for chat history."""

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
    
    def format_for_history(self) -> str:
        """Format the message for history display.
        
        Returns:
            str: Formatted message
        """
        timestamp = self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        return f"[{timestamp}] {self.role}: {self.content}" 
"""Context management for chat history."""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from ..models.message import Message


class ContextManager:
    """Manages conversation history and context."""
    
    def __init__(self, max_history: int = 100, session_name: str = None):
        """Initialize the ContextManager.
        
        Args:
            max_history (int): Maximum number of messages to keep in history
            session_name (str, optional): Custom name for the session files
        """
        self.max_history = max_history
        self.history: List[Message] = []
        self.session_start = datetime.now()
        
        # Ensure cache directory exists
        self.cache_dir = Path.home() / ".cache" / "chatguys"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Set default session files
        if session_name:
            self.session_file = self.cache_dir / f"{session_name}.json"
            self.text_file = self.cache_dir / f"{session_name}.txt"
        else:
            timestamp = self.session_start.strftime('%Y%m%d_%H%M%S')
            self.session_file = self.cache_dir / f"chat_{timestamp}.json"
            self.text_file = self.cache_dir / f"chat_{timestamp}.txt"
    
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
        
        # Save to files
        self._save_history()
    
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
        self._save_history()
    
    def _save_history(self) -> None:
        """Save the conversation history to both JSON and text files."""
        # Save JSON format
        history_data = {
            "session_start": self.session_start.isoformat(),
            "messages": [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat()
                }
                for msg in self.history
            ]
        }
        
        with open(self.session_file, 'w', encoding='utf-8') as f:
            json.dump(history_data, f, indent=2, ensure_ascii=False)
        
        # Save plain text format
        with open(self.text_file, 'w', encoding='utf-8') as f:
            f.write(f"Chat session started at: {self.session_start.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            for msg in self.history:
                timestamp = msg.timestamp.strftime("%Y-%m-%d %H:%M:%S")
                if msg.role == "user":
                    f.write(f"[{timestamp}] You: {msg.content}\n\n")
                else:
                    f.write(f"[{timestamp}] {msg.role}: {msg.content}\n\n")
    
    def format_history(self, last_n: Optional[int] = None) -> str:
        """Format the conversation history for display.
        
        Args:
            last_n (int, optional): Number of most recent messages to include
            
        Returns:
            str: Formatted conversation history
        """
        history = self.get_history(last_n)
        return "\n".join(msg.format_for_history() for msg in history)
    
    def load_history(self, filename: str) -> bool:
        """Load conversation history from a file.
        
        Args:
            filename (str): Name of the file to load (with or without extension)
            
        Returns:
            bool: True if history was loaded successfully, False otherwise
        """
        # Strip extension if provided
        base_name = filename.rsplit('.', 1)[0]
        json_file = self.cache_dir / f"{base_name}.json"
        
        # Update file paths
        self.session_file = json_file
        self.text_file = self.cache_dir / f"{base_name}.txt"
        
        # If file doesn't exist, keep current history (if any) and save to new file
        if not json_file.exists():
            print(f"\nCreating new session: {base_name}")
            # Only save if this is a new session (no history exists)
            if not self.history:
                self._save_history()
            return True
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Load session start time
            self.session_start = datetime.fromisoformat(data['session_start'])
            
            # Load messages with their original timestamps
            loaded_messages = [
                Message(
                    role=msg['role'],
                    content=msg['content'],
                    timestamp=datetime.fromisoformat(msg['timestamp'])
                )
                for msg in data['messages']
            ]
            
            # Merge with existing history if any
            if self.history:
                print("\nMerging with current session...")
                # Add loaded messages that aren't already in history
                existing_timestamps = {msg.timestamp.isoformat() for msg in self.history}
                for msg in loaded_messages:
                    if msg.timestamp.isoformat() not in existing_timestamps:
                        self.history.append(msg)
            else:
                self.history = loaded_messages
            
            # Sort messages by timestamp to ensure correct order
            self.history.sort(key=lambda x: x.timestamp)
            
            # Trim history if it exceeds max_history
            if len(self.history) > self.max_history:
                self.history = self.history[-self.max_history:]
            
            # Display recovery info and messages
            print(f"\nRecovered session from {self.session_start.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Total messages: {len(self.history)}\n")
            
            if self.history:
                print("Conversation history:")
                print("-" * 40)
                for msg in self.history:
                    if msg.role == "user":
                        print(f"\n[{msg.timestamp.strftime('%H:%M:%S')}] You: {msg.content}")
                    elif msg.role == "system":
                        print(f"\n[{msg.timestamp.strftime('%H:%M:%S')}] System: {msg.content}")
                    else:
                        print(f"\n[{msg.timestamp.strftime('%H:%M:%S')}] {msg.role}: {msg.content}")
                print("\n" + "-" * 40 + "\n")
            
            # Save merged history
            self._save_history()
            return True
        except Exception as e:
            print(f"Error loading session: {str(e)}")
            return False 
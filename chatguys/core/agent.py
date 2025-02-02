"""Core agent functionality."""

import os
from typing import Dict, Any, Optional, Tuple
import openai
from openai import AsyncOpenAI

from ..models.message import Message


class Agent:
    """Base agent class that handles OpenAI API interactions."""
    
    def __init__(self, role_name: str, config: Dict[str, Any], default_api_key: str, default_base_url: str):
        """Initialize the agent.
        
        Args:
            role_name (str): Name of the role
            config (Dict[str, Any]): Role configuration
            default_api_key (str): Default OpenAI API key
            default_base_url (str): Default OpenAI base URL
        """
        self.role_name = role_name
        self.config = config
        self.default_api_key = default_api_key
        self.default_base_url = default_base_url
        
        # Initialize OpenAI client
        api_key, base_url = self._get_api_settings()
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url
        )
    
    def _get_api_settings(self) -> Tuple[str, str]:
        """Get API settings for this role.
        
        Returns:
            Tuple[str, str]: (api_key, base_url)
        """
        model_config = self.config.get('model', {})
        
        # Try role-specific environment variables first
        env_key = f"OPENAI_API_KEY_{self.role_name.upper()}"
        env_url = f"OPENAI_BASE_URL_{self.role_name.upper()}"
        
        api_key = (
            model_config.get('openai_api_key') or  # From YAML
            os.getenv(env_key) or                  # From role-specific env
            self.default_api_key                   # Default
        )
        
        base_url = (
            model_config.get('openai_base_url') or  # From YAML
            os.getenv(env_url) or                   # From role-specific env
            self.default_base_url                   # Default
        )
        
        return api_key, base_url
    
    async def get_response(self, message: str, history: list[Message]) -> str:
        """Get a response from the agent.
        
        Args:
            message (str): User message
            history (list[Message]): Conversation history
            
        Returns:
            str: Agent's response
        """
        # Convert history to OpenAI message format
        messages = [{"role": "system", "content": self.config['prompt']}]
        
        # Add a system message to explain the conversation format
        messages.append({
            "role": "system",
            "content": "The conversation history includes context about who messages are addressed to. "
                      "Pay attention to the conversation flow and context when responding."
        })
        
        # Add conversation history
        for msg in history:
            if msg.role == "user":
                messages.append({"role": "user", "content": msg.content})
            else:
                messages.append({"role": "assistant", "content": msg.content})
        
        # Add the current message
        messages.append({"role": "user", "content": message})
        
        try:
            # Call OpenAI API
            response = await self.client.chat.completions.create(
                model=self.config['model']['engine'],
                messages=messages,
                temperature=self.config['model']['temperature'],
                max_tokens=self.config['model']['max_tokens']
            )
            
            return response.choices[0].message.content
        except Exception as e:
            return f"Error getting response from {self.role_name}: {str(e)}" 
"""Configuration management."""

import os
from pathlib import Path
from typing import Dict, Any, Optional, List
import yaml


class ConfigManager:
    """Manages role configurations."""
    
    def __init__(self):
        """Initialize the ConfigManager."""
        self.config_dir = Path.home() / ".config" / "chatguys"
        self.roles: Dict[str, Dict[str, Any]] = {}
        self.load_configurations()
    
    def load_configurations(self) -> None:
        """Load all role configurations."""
        # Ensure config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Load default roles config
        default_config = self.config_dir / "default_roles.yaml"
        if not default_config.exists():
            # Use minimal default config
            self.roles = {
                "Default": {
                    "model": {
                        "provider": "OpenAI",
                        "engine": "gpt-4",
                        "temperature": 0.7,
                        "max_tokens": 300
                    },
                    "prompt": "You are a helpful assistant. Provide clear and concise responses."
                }
            }
            return
        
        try:
            with open(default_config, 'r', encoding='utf-8') as f:
                self.roles = yaml.safe_load(f) or {}
        except Exception as e:
            print(f"Error loading configuration: {str(e)}")
            # Fall back to minimal default config
            self.roles = {
                "Default": {
                    "model": {
                        "provider": "OpenAI",
                        "engine": "gpt-4",
                        "temperature": 0.7,
                        "max_tokens": 300
                    },
                    "prompt": "You are a helpful assistant. Provide clear and concise responses."
                }
            }
    
    def get_role_config(self, role_name: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific role.
        
        Args:
            role_name (str): Name of the role
            
        Returns:
            Optional[Dict[str, Any]]: Role configuration if found, None otherwise
        """
        return self.roles.get(role_name)
    
    def list_roles(self) -> List[str]:
        """Get list of available roles.
        
        Returns:
            List[str]: List of role names
        """
        return list(self.roles.keys()) 
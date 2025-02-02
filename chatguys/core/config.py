"""Configuration management for roles and settings."""

import os
from pathlib import Path
from typing import Dict, Any, Optional
import yaml


class ConfigManager:
    """Manages role configurations and settings."""
    
    def __init__(self, config_dir: str = "config"):
        """Initialize the ConfigManager.
        
        Args:
            config_dir (str): Path to the directory containing YAML configuration files
        """
        self.config_dir = config_dir
        self.roles: Dict[str, Dict[str, Any]] = {}
        self.load_configurations()
    
    def load_configurations(self) -> None:
        """Load and merge all YAML configuration files from the config directory."""
        if not os.path.exists(self.config_dir):
            raise FileNotFoundError(f"Configuration directory {self.config_dir} not found")
        
        # Get all YAML files in the config directory
        yaml_files = sorted(Path(self.config_dir).glob("*.yaml"))
        
        for yaml_file in yaml_files:
            with open(yaml_file, 'r') as f:
                config = yaml.safe_load(f)
                if config:
                    self._merge_config(config)
    
    def _merge_config(self, new_config: Dict[str, Any]) -> None:
        """Merge a new configuration with existing roles.
        
        Args:
            new_config (Dict[str, Any]): New configuration to merge
        """
        for role_name, role_config in new_config.items():
            if role_name in self.roles:
                # Deep merge for existing roles
                self.roles[role_name] = self._deep_merge(
                    self.roles[role_name], role_config
                )
            else:
                # New role, just add it
                self.roles[role_name] = role_config
    
    def _deep_merge(self, dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two dictionaries.
        
        Args:
            dict1 (Dict[str, Any]): Base dictionary
            dict2 (Dict[str, Any]): Dictionary to merge on top
            
        Returns:
            Dict[str, Any]: Merged dictionary
        """
        result = dict1.copy()
        
        for key, value in dict2.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def get_role_config(self, role_name: str) -> Optional[Dict[str, Any]]:
        """Get the configuration for a specific role.
        
        Args:
            role_name (str): Name of the role
            
        Returns:
            Optional[Dict[str, Any]]: Role configuration if it exists, None otherwise
        """
        return self.roles.get(role_name)
    
    def get_default_role(self) -> Optional[Dict[str, Any]]:
        """Get the configuration for the default role.
        
        Returns:
            Optional[Dict[str, Any]]: Default role configuration if it exists, None otherwise
        """
        return self.get_role_config("Default")
    
    def list_roles(self) -> list[str]:
        """Get a list of all available roles.
        
        Returns:
            list[str]: List of role names
        """
        return list(self.roles.keys()) 
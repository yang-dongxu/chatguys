"""ChatGuys - A multi-agent chatbot framework."""

__version__ = "0.1.0"

from .cli.app import ChatApp
from .core.agent import Agent
from .core.config import ConfigManager
from .core.context import ContextManager
from .cli.commands import CommandProcessor
from .cli.input import InputHandler

__all__ = [
    'ChatApp',
    'Agent',
    'ConfigManager',
    'ContextManager',
    'CommandProcessor',
    'InputHandler'
] 
"""ChatGuys - A multi-agent chatbot framework."""

__version__ = "0.1.0"

from .chat_app import ChatApp
from .agent_manager import AgentManager
from .context_manager import ContextManager
from .command_processor import CommandProcessor

__all__ = ['ChatApp', 'AgentManager', 'ContextManager', 'CommandProcessor'] 
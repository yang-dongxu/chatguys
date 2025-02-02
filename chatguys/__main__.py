"""Entry point for running the ChatGuys application."""

import asyncio
from rich.console import Console

from .cli.app import ChatApp


def main():
    """Entry point for the chat application."""
    try:
        app = ChatApp()
        asyncio.run(app.run())
    except (KeyboardInterrupt, asyncio.CancelledError):
        # Handle exit signals gracefully at the top level
        Console().print("\nApplication shut down.")
    except Exception as e:
        Console().print(f"[red]Fatal error:[/red] {str(e)}")
        exit(1)


if __name__ == "__main__":
    main() 
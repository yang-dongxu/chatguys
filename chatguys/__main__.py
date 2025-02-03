"""Entry point for the chatguys package."""

import asyncio
import sys
from pathlib import Path
import shutil
from .cli.app import ChatApp


def ensure_config():
    """Ensure config directory and default files exist."""
    # Get user config directory
    config_dir = Path.home() / ".config" / "chatguys"
    config_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy default config if it doesn't exist
    default_config = config_dir / "default_roles.yaml"
    if not default_config.exists():
        pkg_config = Path(__file__).parent / "config" / "default_roles.yaml"
        if pkg_config.exists():
            shutil.copy(pkg_config, default_config)
        else:
            # Create basic default config
            default_config.write_text("""Default:
  model:
    provider: OpenAI
    engine: gpt-4
    temperature: 0.7
    max_tokens: 300
  prompt: "You are a helpful assistant. Provide clear and concise responses."
""")
    
    # Create .env file if it doesn't exist
    env_file = config_dir / ".env"
    if not env_file.exists():
        env_file.write_text("""# OpenAI settings
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1

# Google settings
GOOGLE_API_KEY=your_google_api_key_here

# Optional: Role-specific API keys
# OPENAI_API_KEY_TECH=your_tech_role_api_key
# GOOGLE_API_KEY_CREATIVE=your_creative_role_api_key
""")
        print(f"Please configure your API keys in {env_file}")


def main():
    """Main entry point for the chatguys package."""
    try:
        # Ensure config exists
        ensure_config()
        
        # Create and run the app
        app = ChatApp()
        asyncio.run(app.run())
        return 0
    except KeyboardInterrupt:
        print("\nGoodbye!")
        return 0
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main()) 
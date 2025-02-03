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
    
    # Create .env file if it doesn't exist
    env_file = config_dir / ".env"
    if not env_file.exists():
        env_file.write_text("""# OpenAI settings
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1

# Optional: Role-specific API keys
# OPENAI_API_KEY_TECH=your_tech_role_api_key
# OPENAI_API_KEY_CREATIVE=your_creative_role_api_key
""")
        print(f"\nConfiguration files created in {config_dir}")
        print(f"Please configure your API keys in {env_file}")
        return False
    
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
    engine: gpt-3.5-turbo
    temperature: 0.7
    max_tokens: 300
  prompt: "You are a helpful assistant. Provide clear and concise responses."

Tech:
  model:
    engine: gpt-4
    temperature: 0.3
    max_tokens: 500
  prompt: "You are a technical expert. Provide detailed technical explanations and code examples."

Creative:
  model:
    engine: gpt-4
    temperature: 0.8
    max_tokens: 800
  prompt: "You are a creative assistant. Think outside the box and provide imaginative responses."
""")
    
    return True


def main():
    """Main entry point for the chatguys package."""
    try:
        # Ensure config exists
        if not ensure_config():
            return 1
        
        # Create and run the app
        app = ChatApp()
        asyncio.run(app.run())
        return 0
    except KeyboardInterrupt:
        print("\nGoodbye!")
        return 0
    except ValueError as e:
        print(f"\nConfiguration Error: {str(e)}")
        return 1
    except Exception as e:
        print(f"\nError: {str(e)}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main()) 
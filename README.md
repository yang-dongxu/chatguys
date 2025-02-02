# ChatGuys

A flexible multi-agent chatbot framework that supports role-based conversations and dynamic configuration through YAML files.

## Features

- Multiple agent roles with different personalities and capabilities
- Dynamic configuration through YAML files
- Role-specific OpenAI API keys and base URLs
- Shared conversation history between agents
- System commands for managing the chat session
- Rich text output with markdown support
- Easy role switching using @mentions

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/chatguys.git
cd chatguys
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

4. Set up your environment:
   - Copy `.env.example` to `.env`:
     ```bash
     cp .env.example .env
     ```
   - Edit `.env` and set your OpenAI API key and other optional settings:
     ```
     OPENAI_API_KEY=your_api_key_here
     OPENAI_BASE_URL=https://api.openai.com/v1  # Optional: custom base URL
     ```
   - You can also set role-specific API keys and base URLs if needed:
     ```
     OPENAI_API_KEY_TECH=your_tech_role_api_key_here
     OPENAI_BASE_URL_TECH=https://custom-endpoint/v1
     ```

## Usage

1. Start the chat application:
```bash
python -m chatguys
```

2. Use system commands:
- `/help` - Show help information
- `/reset` - Clear conversation history
- `/reload` - Reload agent configurations
- `/roles` - List available roles
- `/quit` or `/exit` - Exit the application

3. Chat with specific agents using @mentions:
```
@Tech How do I implement a binary search?
@Creative Tell me a story about a robot.
```

4. Messages without @mentions will be handled by the default agent.

5. You can mention multiple agents in one message to get responses from all of them:
```
@Tech @Default @Creative how would you describe the internet to someone from the 1800s?
```

## Configuration

Agents are configured through YAML files in the `config` directory. The system loads and merges these files in alphabetical order.

Example configuration (`config/default_roles.yaml`):
```yaml
Default:
  model:
    provider: OpenAI
    engine: gpt-4
    temperature: 0.5
    max_tokens: 300
    # Optional: override OpenAI settings
    # openai_api_key: your_api_key_here  # If not set, uses OPENAI_API_KEY from .env
    # openai_base_url: https://api.openai.com/v1  # If not set, uses OPENAI_BASE_URL from .env
  prompt: "You are the default agent. Provide clear, balanced responses."

Tech:
  model:
    provider: OpenAI
    engine: gpt-4
    temperature: 0.3  # Lower temperature for more precise responses
    max_tokens: 300
    # Example of role-specific API settings
    # openai_api_key: tech_role_api_key_here
    # openai_base_url: https://custom-endpoint/v1
  prompt: "You are the Tech agent. Answer with technical details."
```

You can add more YAML files to override or extend the configuration. Each role can have its own OpenAI API key and base URL, which will override the default settings from the `.env` file. This is useful when you want to:

- Use different API keys for different roles (e.g., for billing or rate limiting purposes)
- Connect to different OpenAI-compatible endpoints for specific roles
- Use a mix of official OpenAI API and self-hosted models

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 
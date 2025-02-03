# ChatGuys

A flexible multi-agent chatbot framework that supports role-based conversations with OpenAI models.

## Features

- Multiple agent roles with different personalities and capabilities
- Dynamic configuration through YAML files
- Role-specific OpenAI API keys
- Shared conversation history between agents
- System commands for managing the chat session
- Rich text output with markdown support
- Easy role switching using @mentions
- Automatic chat history saving in both JSON and plain text formats

## Installation

### Using pipx (Recommended)

```bash
# Install pipx if you haven't already
python -m pip install --user pipx
pipx ensurepath

# Install chatguys
pipx install chatguys
```

### From Source

1. Clone the repository:
```bash
git clone https://github.com/yourusername/chatguys.git
cd chatguys
```

2. Install using pipx in editable mode:
```bash
pipx install -e .
```

## Configuration

When you first run `chatguys`, it will create the necessary configuration files in `~/.config/chatguys/`:

1. API Keys (`.env`):
   ```bash
   # OpenAI settings
   OPENAI_API_KEY=your_api_key_here
   OPENAI_BASE_URL=https://api.openai.com/v1
   
   # Optional: Role-specific API keys
   # OPENAI_API_KEY_TECH=your_tech_role_api_key
   # OPENAI_API_KEY_CREATIVE=your_creative_role_api_key
   ```

2. Role Configuration (`default_roles.yaml`):
   ```yaml
   Default:
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
   ```

## Usage

1. Start the chat application:
```bash
chatguys
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

5. You can use mentions in different ways:
   - Same message to multiple agents (mentions at start or end):
     ```
     @Tech @Creative how would you describe the internet?
     ```
     or
     ```
     Tell me about AI @Tech @Creative
     ```
   - Different messages to different agents (mentions throughout):
     ```
     @Tech explain how databases work. @Creative write a story about a database.
     ```

## Chat History

Your chat histories are automatically saved in `~/.cache/chatguys/`:
1. JSON format for programmatic use:
   ```
   ~/.cache/chatguys/chat_YYYYMMDD_HHMMSS.json
   ```
2. Plain text format for easy reading:
   ```
   ~/.cache/chatguys/chat_YYYYMMDD_HHMMSS.txt
   ```

The file locations will be displayed when you exit the application.

## File Locations

- Configuration: `~/.config/chatguys/`
  - `.env` - API keys and settings
  - `default_roles.yaml` - Role configurations
- Chat History: `~/.cache/chatguys/`
  - `chat_YYYYMMDD_HHMMSS.json` - JSON format
  - `chat_YYYYMMDD_HHMMSS.txt` - Plain text format

## Model Support

- Supports all OpenAI chat models:
  - gpt-3.5-turbo (default for basic queries)
  - gpt-4 (default for Tech and Creative roles)
  - Any other available OpenAI chat models
- Configurable parameters per role:
  - temperature (creativity level)
  - max_tokens (response length)
  - custom prompts

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 
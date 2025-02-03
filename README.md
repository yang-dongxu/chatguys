# ChatGuys

A flexible multi-agent chatbot framework that supports role-based conversations and dynamic configuration through YAML files.

## Features

- Multiple agent roles with different personalities and capabilities
- Support for both OpenAI and Google's Gemini models
- Dynamic configuration through YAML files
- Role-specific API keys and base URLs
- Shared conversation history between agents
- System commands for managing the chat session
- Rich text output with markdown support
- Easy role switching using @mentions
- Automatic chat history saving in both JSON and plain text formats
- Support for Gemini's experimental search with reference links

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

### Configuration

All configuration files are stored in `~/.config/chatguys/`:

1. API Keys (`.env`):
   ```bash
   # OpenAI settings
   OPENAI_API_KEY=your_api_key_here
   OPENAI_BASE_URL=https://api.openai.com/v1
   
   # Google settings
   GOOGLE_API_KEY=your_google_api_key_here
   
   # Optional: Role-specific API keys
   OPENAI_API_KEY_TECH=your_tech_role_api_key_here
   GOOGLE_API_KEY_CREATIVE=your_creative_role_api_key_here
   ```

2. Role Configuration (`default_roles.yaml`):
   ```yaml
   Default:
     model:
       provider: OpenAI
       engine: gpt-4
       temperature: 0.5
       max_tokens: 300
     prompt: "You are the default agent. Provide clear, balanced responses."

   Tech:
     model:
       provider: OpenAI
       engine: gpt-4
       temperature: 0.3
       max_tokens: 300
     prompt: "You are the Tech agent. Answer with technical details."
   
   Creative:
     model:
       provider: google
       engine: gemini-2.0-flash-exp-search
       temperature: 0.7
     prompt: "You are the Creative agent. Be imaginative and inspiring."
   ```

When you first run `chatguys`, it will create these configuration files if they don't exist. You'll need to edit them to add your API keys and customize the roles.

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
   - Same message to multiple agents (mentions at start):
     ```
     @Tech @Creative @Default how would you describe the internet?
     ```
   - Different messages to different agents (mentions throughout):
     ```
     @Tech explain how databases work. @Creative write a story about a database.
     ```
   - Mentions at the end:
     ```
     Tell me about AI @Tech @Creative
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

## Model Support

### OpenAI Models
- Supports all OpenAI chat models (gpt-3.5-turbo, gpt-4, etc.)
- Configurable temperature and max tokens
- Support for custom API endpoints

### Google Gemini Models
- Supports all Gemini models including:
  - gemini-pro
  - gemini-2.0-flash-exp-search (with reference links)
- Automatic reference extraction and formatting for search results

## File Locations

- Configuration: `~/.config/chatguys/`
  - `.env` - API keys and settings
  - `default_roles.yaml` - Role configurations
- Chat History: `~/.cache/chatguys/`
  - `chat_YYYYMMDD_HHMMSS.json` - JSON format
  - `chat_YYYYMMDD_HHMMSS.txt` - Plain text format

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 
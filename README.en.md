# AI Multi-Agent Toolkit

<div align="center">
  <img src="docs/image.png" alt="AI Multi-Agent Toolkit" width="800"/>
</div>

A comprehensive toolkit for developing Python-based LLM agents with practical examples. Supports multiple LLM provider integration, speech-to-text conversion, Discord integration, and more.

**📖 Documentation:** https://jih4855.github.io/AI-Multi-Agent-Toolkit/
**📁 Repository:** https://github.com/jih4855/AI-Multi-Agent-Toolkit

## Key Features

- **Multi-LLM Support**: Integrated Ollama, OpenAI, and Google Gemini
- **Agent System**: Single/multi-agent pattern support
- **Speech Processing**: Whisper-based STT (Speech-to-Text)
- **Discord Integration**: Message sending via webhooks (chunk splitting support)
- **Conversation Memory**: SQLite-based context management
- **Documentation**: Dark theme HTML documentation
- **Multimodal Support**: Vision + language models for image analysis

## System Requirements

- Python 3.10 or higher
- pip (package manager)
- ffmpeg (required for audio processing, optional)

## Installation

### 1. Clone Repository
```bash
git clone https://github.com/jih4855/AI-Multi-Agent-Toolkit.git
cd AI-Multi-Agent-Toolkit
```

### 2. Create Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Variables Setup
```bash
# Copy .env.example to .env
cp .env.example .env

# Edit .env file with your actual API keys
# GOOGLE_API_KEY=your_google_api_key_here
# OPENAI_API_KEY=your_openai_api_key_here
# DISCORD_WEBHOOK_URL=your_discord_webhook_url_here
```

**Note:** No API key required when using Ollama.

## Quick Start

### Basic LLM Agent Usage
```python
from module.llm_agent import LLM_Agent

# Using Ollama (local, no API key required)
agent = LLM_Agent(model_name="gemma:2b", provider="ollama")
response = agent.generate_response(
    system_prompt="You are a helpful assistant.",
    user_message="Hello, please introduce yourself."
)
print(response)
```

### API Integration with Environment Variables
```python
import os
from dotenv import load_dotenv
from module.llm_agent import LLM_Agent

load_dotenv()

# Using Google Gemini
agent = LLM_Agent(
    model_name="gemini-2.5-flash",
    provider="genai",
    api_key=os.getenv("GOOGLE_API_KEY")
)

response = agent.generate_response(
    system_prompt="You are a helpful assistant.",
    user_message="Explain machine learning in simple terms."
)
print(response)
```

## Usage Examples

### 1. Multi-Agent Collaboration

```python
from module.llm_agent import LLM_Agent

system_prompt = "You are a helpful assistant."
agent1_user_prompt = "Please explain Linux."
agent2_user_prompt = "Read the previous answer and supplement the content."

# Define multiple agent prompts
multi_agent = LLM_Agent(model_name="gemma3n", provider="ollama")
agent1 = multi_agent(system_prompt, agent1_user_prompt, task=None)
agent2 = multi_agent(system_prompt, agent2_user_prompt, task=None, multi_agent_response=agent1)

print("Agent 1 Response:", agent1)
print("Agent 2 Response:", agent2)
```

### 2. Integrating All Agent Responses

```python
from module.llm_agent import LLM_Agent

# Define system prompts, user prompts, and tasks for each agent
multi_agent_tasks = {
    "Agent 1": "Organize environmental problems (air, water, waste, etc.) occurring in cities and present the most urgent challenges.",
    "Agent 2": "Propose sustainable transportation infrastructure plans based on eco-friendly transportation (public transport, bicycles, electric vehicles, etc.).",
    "Agent 3": "Design efficient energy supply plans using renewable energy (solar, wind, smart grid, etc.).",
    "Agent 4": "Optimize urban spatial structure (parks, residential, commercial area layout, etc.)."
}

multi_agent_system_prompts = {
    "Agent 1": "You are an environmental expert. Analyze urban environmental problems and present the most urgent issues.",
    "Agent 2": "You are a transportation expert. Propose sustainable transportation infrastructure plans.",
    "Agent 3": "You are an energy expert. Design energy supply plans using renewable energy.",
    "Agent 4": "You are an urban planning expert. Present ways to optimize urban spatial structure."
}

user_prompts = {
    "Agent 1": "Analyze environmental problems occurring in cities and present the most urgent issues.",
    "Agent 2": "Propose sustainable transportation infrastructure plans.",
    "Agent 3": "Design energy supply plans using renewable energy.",
    "Agent 4": "Present ways to optimize urban spatial structure."
}

order = ["Agent 1", "Agent 2", "Agent 3", "Agent 4"]

multi_agent = LLM_Agent(model_name="gemini-2.5-flash", provider="genai", api_key="your_api_key")

agent_responses = {
    name: multi_agent(multi_agent_system_prompts[name], user_prompts[name], multi_agent_tasks[name])
    for name in order
}

response_list = [agent_responses[name] for name in order]

multi_agent_responses = multi_agent(
    "You are an urban planning expert. Present sustainable urban design plans.",
    "Here are opinions from various experts. Based on this, present a final summary and integrated sustainable urban design plan.",
    "Present a final summary and integrated sustainable urban design plan.",
    response_list
)

print("Agent 1 Response:", agent_responses["Agent 1"])
print("Agent 2 Response:", agent_responses["Agent 2"])
print("Agent 3 Response:", agent_responses["Agent 3"])
print("Agent 4 Response:", agent_responses["Agent 4"])
print("Multi-Agent Responses:", multi_agent_responses)
```

### 3. Adding Memory to LLM Agent

```python
import dotenv
import os
dotenv.load_dotenv()

# Create LLM_Agent instance
llm = LLM_Agent(model_name="gemini-2.5-flash", provider="genai", api_key=os.getenv("GENAI_API_KEY"), max_history=10)

# Conversation loop example
while True:
    user_input = input("You: ")
    response = llm(system_prompt="You are a helpful assistant.", user_message=user_input, memory=True)
    print("Assistant:", response)

    if user_input.lower() in ['exit', 'quit']:
        break
```

### 4. Multimodal Agent for Image Analysis

```python
import os
from dotenv import load_dotenv
from module.llm_agent import Multi_modal_agent

load_dotenv()

# Create multimodal agent
agent = Multi_modal_agent(
    model_name="gemini-2.5-flash",
    provider="genai",
    api_key=os.getenv("GOOGLE_API_KEY")
)

# Analyze image with structured JSON output
response = agent.analyze_image(
    image_path="path/to/your/image.jpg",
    system_prompt="""Analyze the image and extract text content.
    Please respond in the following JSON format:
    {
        "extracted_text": "text content found in the image",
        "confidence": "high/medium/low",
        "language": "detected language",
        "additional_notes": "any additional observations"
    }""",
    user_message="Please extract and organize the text content from this image."
)

print("Analysis Result:", response)
```

### 5. Sending Messages to Discord

```python
from module.discord import Send_to_discord
from module.llm_agent import LLM_Agent

model_name = 'gemma3:12b'
system_prompt = 'You are a capable assistant. Provide helpful answers to users.'
user_prompt = 'What is the capital of France?'
provider = 'ollama'

agent = LLM_Agent(model_name, provider, api_key=None)
response = agent(system_prompt, user_prompt, task=None)

discord = Send_to_discord(base_url="your_discord_webhook_url")
discord.send_message(response)
```

## Project Structure

```
agent/
├── module/                 # Core libraries
│   ├── llm_agent.py       # LLM agent classes
│   ├── audio_tool.py      # Audio processing tools
│   ├── discord.py         # Discord integration
│   ├── memory.py          # Conversation memory management
│   └── text_tool.py       # Text processing utilities
├── test/                  # Usage examples and tests
├── docs/                  # HTML documentation
│   ├── index.html         # Detailed usage guide
│   ├── styles.css         # Documentation styling
│   └── scripts.js         # Interactive features
├── .env.example           # Environment variables template
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation (Korean)
└── README.en.md          # Project documentation (English)
```

## API Key Setup

### Google Gemini API
1. Get API key from [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Add `GOOGLE_API_KEY=your_key` to `.env` file

### OpenAI API
1. Get API key from [OpenAI Platform](https://platform.openai.com/api-keys)
2. Add `OPENAI_API_KEY=your_key` to `.env` file

### Discord Webhook (Optional)
1. Create webhook in Discord server settings > Integrations > Webhooks
2. Add `DISCORD_WEBHOOK_URL=your_webhook_url` to `.env` file

## Documentation

Check detailed usage and examples in online documentation:

**📖 Online Documentation:** https://jih4855.github.io/AI-Multi-Agent-Toolkit/

Or open `docs/index.html` locally in your browser:

```bash
# Open local documentation in browser
open docs/index.html    # macOS
start docs/index.html   # Windows
xdg-open docs/index.html # Linux
```

**Documentation Contents:**
- Step-by-step installation guide and environment setup
- Basic LLM agent usage
- Multi-agent system configuration methods
- Speech-to-text conversion practice
- Discord message sending and chunk splitting
- Conversation context memory features
- Multimodal image analysis examples
- Troubleshooting and problem-solving guides

## Testing

```bash
# Run specific test files
python test/chat_llm_test.py          # Chat with memory test
python test/multi_modal_test.py       # Multimodal analysis test
python test/nano_banana_test.py       # Basic functionality test
```

## Common Issues

**ModuleNotFoundError**
```bash
# Solution: Check virtual environment activation and reinstall dependencies
pip install -r requirements.txt
```

**API Key Related Errors**
```bash
# Solution: Check .env file configuration
cat .env  # Check configured environment variables
```

**Ollama Connection Error**
```bash
# Solution: Check Ollama service running
ollama list  # Check installed models
```

**Audio Processing Error**
```bash
# Solution: Install ffmpeg
# Windows (Chocolatey):
choco install ffmpeg

# macOS (Homebrew):
brew install ffmpeg

# Ubuntu/Debian:
sudo apt install ffmpeg

# Verify installation:
ffmpeg -version
```

**CUDA Compatibility on Apple Silicon**
```bash
# Solution: Install appropriate packages for Apple Silicon
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

## Support

- 📖 [Documentation](https://jih4855.github.io/AI-Multi-Agent-Toolkit/)
- 🐛 [Issues](https://github.com/jih4855/AI-Multi-Agent-Toolkit/issues)
- 💬 [Discussions](https://github.com/jih4855/AI-Multi-Agent-Toolkit/discussions)
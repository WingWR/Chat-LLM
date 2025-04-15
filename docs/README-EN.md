# Chat-LLM - Multi-Model Supported Chat Interface

A multi-turn conversation web application based on [Gradio](https://www.gradio.app/) that supports streaming responses, historical conversation management, and multi-model switching.

[中文版](README.md) | [English](READEME-EN.md)

## Features
- ✅ Supports multiple and custom models
- 🧠 Retains context in multi-turn conversations
- 🔄 Real-time streaming output
- 📚 History session management (view/switch/delete)

## Core Libraries
The following third-party libraries are used:
- Gradio
- openai
- dotenv
- Standard libraries such as typing, uuid, json, etc.

## Custom Models
Set up models and API keys in `module_config.py`:
```json
"OpenAI": {
        "api_key": "yourOpenAIkey",
        "base_url": "base_url",
        "model_name": "gpt-3.5-turbo"
    }
```

## Running the Application
```bash
python web.py
```

## Authors
Lei Wang
Haotian Li
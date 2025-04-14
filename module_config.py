import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 模型配置
MODELS = {
    "DeepSeek": {
        "api_key": os.getenv("DEEPSEEK_API_KEY"),
        "base_url": "https://api.deepseek.com",
        "model_name": "deepseek-chat"
    },
    "OpenAI": {
        "api_key": os.getenv("OPENAI_API_KEY"),
        "base_url": "https://api.openai.com/v1",
        "model_name": "gpt-3.5-turbo"
    }
}
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
    "Qwen": {
        "api_key": os.getenv("DASHSCOPE_API_KEY"),
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "model_name": "qwq-plus"
    },
    "ChatGpt": {
        "api_key": os.getenv("OPENAI_API_KEY"),
        "base_url": "https://api.openai.com/v1",
        "model_name": "GPT-4o mini"
    },
}

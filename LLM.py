import uuid
import datetime
import gradio as gr
from openai import OpenAI
from module_config import MODELS
from typing import List, Dict, Tuple, Generator, Union
from openai.types.chat import ChatCompletion, ChatCompletionChunk


# 对话历史存储
conversations = {}
current_conversation_id = None


def get_client(model: str) -> OpenAI:
    """创建指定模型的客户端"""
    config = MODELS[model]
    return OpenAI(
        api_key=config["api_key"],
        base_url=config["base_url"]
    )


def get_current_conversation() -> Dict:
    global current_conversation_id, conversations
    if current_conversation_id is None:
        new_conversation()
    return conversations[current_conversation_id]


def new_conversation() -> str:
    global current_conversation_id, conversations
    conv_id = str(uuid.uuid4())
    conversations[conv_id] = {
        "id": conv_id,
        "title": f"新对话 {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "messages": [{"role": "system", "content": "You are a helpful assistant."}],
        "model": "DeepSeek"
    }
    current_conversation_id = conv_id
    return conv_id


def call_model_api(
    model: str,
    messages: List[Dict[str, str]],
    stream: bool
) -> Union[str, ChatCompletion, Generator[ChatCompletionChunk, None, None]]:  # 用 Generator 替代直接 Stream
    # ... 其他代码不变 ...
    """使用OpenAI SDK调用API"""
    if model not in MODELS:
        return f"错误: 未知模型 {model}"

    if not MODELS[model]["api_key"]:
        return f"错误: 未配置 {model} API 密钥"

    try:
        client = get_client(model)
        response = client.chat.completions.create(
            model=MODELS[model]["model_name"],
            messages=messages,
            temperature=0.7,
            max_tokens=2048,
            stream=stream
        )
        return response
    except Exception as e:
        return f"API调用出错: {str(e)}"


def chat_with_history(
    user_input: str,
    chat_history: List[Dict[str, str]],
    model: str,
) -> Generator[Tuple[str, List[Dict[str, str]]], None, None]:
    """处理对话并获取回复（适配 type='messages' 格式）"""
    conversation = get_current_conversation()

    # 更新对话标题（如果是第一条用户消息）
    if len(conversation["messages"]) == 1:  # 只有system消息
        conversation["title"] = user_input[:30] + "..." if len(user_input) > 30 else user_input

    # 添加用户消息
    conversation["messages"].append({"role": "user", "content": user_input})

    # 调用API
    api_response = call_model_api(model, conversation["messages"], stream=True)

    # 如果是错误消息，直接返回
    if isinstance(api_response, str):
        chat_history.append({"role": "user", "content": user_input})
        chat_history.append({"role": "assistant", "content": api_response})
        yield "", chat_history
        return

    # 流式处理
    chat_history.append({"role": "user", "content": user_input})  # 先添加用户消息
    chat_history.append({"role": "assistant", "content": ""})  # 初始化空AI回复
    partial_message = ""

    # 遍历流式响应
    for chunk in api_response:
        if hasattr(chunk, 'choices') and chunk.choices and chunk.choices[0].delta.content:
            partial_message += chunk.choices[0].delta.content
            # 更新最后一条消息（AI回复）
            chat_history[-1]["content"] = partial_message
            yield "", chat_history  # 返回更新后的聊天记录

    # 流式结束后，保存完整消息到对话历史
    conversation["messages"].append({"role": "assistant", "content": partial_message})


def load_conversation(conv_id: str) -> Tuple[List[Dict[str, str]], str]:
    """加载特定对话（适配 type='messages' 格式）"""
    global current_conversation_id
    current_conversation_id = conv_id
    conversation = conversations[conv_id]

    # 转换为Gradio格式 (跳过system消息)
    chat_history = []
    messages = conversation["messages"][1:]  # 跳过system消息
    for i in range(0, len(messages) - 1, 2):
        if messages[i]['role'] == 'user' and i + 1 < len(messages):
            user_msg = {"role": "user", "content": messages[i]['content']}
            bot_msg = {"role": "assistant", "content": messages[i + 1]['content']}
            chat_history.extend([user_msg, bot_msg])  # 依次添加用户和AI消息

    return chat_history, conversation["model"]


def update_conversation_list():
    """更新对话列表"""
    return gr.update(choices=[(conv["title"], conv["id"]) for conv in sorted(
        conversations.values(),
        key=lambda x: len(x["messages"]),
        reverse=True
    )], value=current_conversation_id)


def delete_conversation(conv_id: str):
    """删除对话"""
    global current_conversation_id
    if conv_id in conversations:
        del conversations[conv_id]
        if current_conversation_id == conv_id:
            current_conversation_id = new_conversation()
    return update_conversation_list()

import gradio as gr
from openai import OpenAI
import os
from typing import List, Dict, Tuple, Generator
import uuid
import datetime
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

# 对话历史存储
conversations = {}
current_conversation_id = None


def get_client(model: str):
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


def new_conversation():
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


def call_model_api(model: str, messages: List[Dict[str, str]], stream: bool) -> Generator[str, None, None] or str:
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

        if stream:
            # 对于流式响应，我们返回一个生成器
            return response
        else:
            # 对于非流式响应，直接返回完整内容
            return response.choices[0].message.content
    except Exception as e:
        return f"API调用出错: {str(e)}"


def chat_with_history(
    user_input: str,
    chat_history: List[Dict[str, str]],  # 改为字典列表格式
    model: str,
    stream: bool
) -> Generator[Tuple[str, List[Dict[str, str]]], None, None] or Tuple[str, List[Dict[str, str]]]:
    """处理对话并获取回复（适配 type='messages' 格式）"""
    conversation = get_current_conversation()

    # 更新对话标题（如果是第一条用户消息）
    if len(conversation["messages"]) == 1:  # 只有system消息
        conversation["title"] = user_input[:30] + "..." if len(user_input) > 30 else user_input

    # 添加用户消息
    conversation["messages"].append({"role": "user", "content": user_input})

    # 调用API
    api_response = call_model_api(model, conversation["messages"], stream)

    if stream:
        # 流式处理
        chat_history.append({"role": "user", "content": user_input})  # 先添加用户消息
        chat_history.append({"role": "assistant", "content": ""})  # 初始化空AI回复
        partial_message = ""

        # 遍历流式响应
        for chunk in api_response:
            if chunk.choices[0].delta.content:
                partial_message += chunk.choices[0].delta.content
                # 更新最后一条消息（AI回复）
                chat_history[-1]["content"] = partial_message
                yield "", chat_history  # 返回更新后的聊天记录

        # 流式结束后，保存完整消息到对话历史
        conversation["messages"].append({"role": "assistant", "content": partial_message})
    else:
        # 非流式处理
        bot_response = api_response
        # 添加助手回复
        conversation["messages"].append({"role": "assistant", "content": bot_response})
        # 返回Gradio格式 (清空输入框, 更新聊天历史)
        chat_history.append({"role": "user", "content": user_input})
        chat_history.append({"role": "assistant", "content": bot_response})
        return "", chat_history


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


# 创建Gradio界面
with gr.Blocks(title="DeepSeek 聊天助手", css="""
    .gradio-container { max-width: 1200px !important }
    .conversation-list { height: 500px !important; overflow-y: auto !important }
""") as demo:
    with gr.Row():
        # 左侧边栏
        with gr.Column(scale=1, min_width=250):
            gr.Markdown("### 模型设置")
            model_dropdown = gr.Dropdown(
                choices=list(MODELS.keys()),
                value="DeepSeek",
                label="选择模型"
            )

            # 添加流式输出开关
            stream_checkbox = gr.Checkbox(
                label="启用流式输出",
                value=True,
                interactive=True
            )

            gr.Markdown("### 对话管理")
            with gr.Row():
                new_chat_btn = gr.Button("+ 新对话", variant="primary")
                delete_btn = gr.Button("🗑️", variant="secondary")

            conversation_list = gr.Radio(
                label="历史对话",
                interactive=True,
                elem_classes=["conversation-list"]
            )

        # 右侧主聊天区
        with gr.Column(scale=4):
            chatbot = gr.Chatbot(
                elem_id="chatbot",
                height=600,
                show_copy_button=True,
                type="messages"
            )

            with gr.Row():
                message = gr.Textbox(
                    placeholder="输入消息...",
                    show_label=False,
                    container=False,
                    autofocus=True,
                    scale=7
                )
                submit_btn = gr.Button("发送", variant="primary", scale=1)

            gr.Markdown("""
            <div style="text-align: center; color: #888; margin-top: 10px;">
            注意: AI可能会产生不准确或误导性的信息
            </div>
            """)

    # 组件交互
    submit_btn.click(
        fn=chat_with_history,
        inputs=[message, chatbot, model_dropdown, stream_checkbox],
        outputs=[message, chatbot]
    ).then(
        fn=update_conversation_list,
        outputs=conversation_list
    )

    message.submit(
        fn=chat_with_history,
        inputs=[message, chatbot, model_dropdown, stream_checkbox],
        outputs=[message, chatbot]
    ).then(
        fn=update_conversation_list,
        outputs=conversation_list
    )

    new_chat_btn.click(
        fn=new_conversation,
        outputs=None
    ).then(
        fn=lambda: ([], "DeepSeek"),
        outputs=[chatbot, model_dropdown]
    ).then(
        fn=update_conversation_list,
        outputs=conversation_list
    )

    conversation_list.change(
        fn=load_conversation,
        inputs=conversation_list,
        outputs=[chatbot, model_dropdown]
    )

    delete_btn.click(
        fn=delete_conversation,
        inputs=conversation_list,
        outputs=conversation_list
    ).then(
        fn=lambda: ([], "DeepSeek"),
        outputs=[chatbot, model_dropdown]
    )

    # 初始化
    demo.load(
        fn=new_conversation,
        outputs=None
    ).then(
        fn=update_conversation_list,
        outputs=conversation_list
    )

if __name__ == "__main__":
    demo.launch()

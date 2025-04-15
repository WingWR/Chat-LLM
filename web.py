import os
from LLM import (
    gr,
    MODELS,
    chat_with_history,
    new_conversation,
    update_conversation_list,
    load_conversation,
    delete_conversation,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # 当前脚本的所在目录
css_path = os.path.join(BASE_DIR, "style.css")

# 创建Gradio界面
with gr.Blocks(
    title = "Whisper", 
    css = open(css_path).read()
) as window:

    # 左侧边栏
    with gr.Row():
        with gr.Column(scale = 1, min_width = 250):
            gr.Markdown("### 模型选择")
            model_dropdown = gr.Dropdown(
                choices = list(MODELS.keys()), 
                value = "DeepSeek", 
                label = "当前模型"
            )

            gr.Markdown("### 对话管理")
            with gr.Row():
                new_chat_btn = gr.Button("+ 新建对话", variant="primary")
                delete_btn = gr.Button("- 清空对话", variant="secondary")

            conversation_list = gr.Radio(
                label = "历史对话", 
                interactive = True, 
                elem_classes = ["conversation-list"]
            )

        # 右侧主聊天区
        with gr.Column(scale = 4):
            chatbot = gr.Chatbot(
                height = 500, 
                show_copy_button = True, 
                type = "messages",
                elem_classes = "chatbox"
            )

            with gr.Tab("文字消息"):
                with gr.Row():
                    message = gr.Textbox(
                        placeholder = "输入消息...",
                        show_label = False,
                        container = False,
                        autofocus = True,
                    )
                    submit_btn = gr.Button("发送", variant="primary", scale=1)

            with gr.Tab("图片消息"):
                with gr.Row():
                    image = gr.Image(
                        show_fullscreen_button = False,
                        elem_classes = "image-input"
                    )
                    submit_btn_2 = gr.Button("发送", variant="primary", scale=1)

            with gr.Tab("音频消息"):
                with gr.Row():
                    audio = gr.Audio(
                        elem_classes = "audio-input"
                    )
                    submit_btn_3 = gr.Button("发送", variant="primary", scale=1)

                

    # 组件交互
    submit_btn.click(
        fn=chat_with_history,
        inputs=[message, chatbot, model_dropdown],
        outputs=[message, chatbot]
    ).then(
        fn=update_conversation_list,
        outputs=conversation_list
    )

    message.submit(
        fn=chat_with_history,
        inputs=[message, chatbot, model_dropdown],
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
    window.load(fn = new_conversation, outputs = None).then(
        fn = update_conversation_list, 
        outputs = conversation_list
    )

if __name__ == "__main__":
    window.launch(share=True)
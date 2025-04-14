from LLM import (
    gr,
    MODELS,
    chat_with_history,
    new_conversation,
    update_conversation_list,
    load_conversation,
    delete_conversation
)

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
    demo.launch(share=True)
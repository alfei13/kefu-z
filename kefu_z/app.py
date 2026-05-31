import gradio as gr
from kefu_z.gateway import Orchestrator
from kefu_z.config import Config
import structlog

structlog.configure(processors=[structlog.dev.ConsoleRenderer()])

orchestrator = None


def init_orchestrator():
    global orchestrator
    if orchestrator is None:
        config = Config()
        orchestrator = Orchestrator(config)


def chat(message, chat_history, user_id):
    init_orchestrator()
    session_id = f"user_{user_id}"
    try:
        reply = orchestrator.process(message, session_id=session_id, user_id=int(user_id))
        chat_history = chat_history or []
        chat_history.append((message, reply))
        return "", chat_history
    except Exception as e:
        chat_history = chat_history or []
        chat_history.append((message, f"抱歉，系统出现异常：{str(e)}"))
        return "", chat_history


def main():
    init_orchestrator()
    config = Config()

    with gr.Blocks(title="AI电商客服系统 V2") as demo:
        gr.Markdown(
            "# 🤖 AI电商客服系统 V2\n"
            "多智能体架构 | ReAct循环 | Agent协作 | 情感识别 | 人工转接\n"
            "---"
        )

        with gr.Row():
            user_id_input = gr.Number(value=1, label="用户ID", precision=0, minimum=1)

        chatbot = gr.Chatbot(height=500, show_copy_button=True)
        msg_input = gr.Textbox(
            placeholder="请输入您的问题，例如：我想买手机、查订单、有优惠券吗、我要退货...",
            show_label=False,
            scale=4,
        )

        with gr.Row():
            send_btn = gr.Button("发送", variant="primary", scale=1)
            clear_btn = gr.Button("清空对话", scale=1)

        def respond(message, chat_history, user_id):
            return chat(message, chat_history, user_id)

        msg_input.submit(respond, [msg_input, chatbot, user_id_input], [msg_input, chatbot])
        send_btn.click(respond, [msg_input, chatbot, user_id_input], [msg_input, chatbot])
        clear_btn.click(lambda: [], None, chatbot)

        gr.Examples(
            examples=[
                "你好，我想买一部手机，有什么推荐？",
                "这个iPhone 16 Pro的详细参数是什么？",
                "查一下我的订单",
                "有没有优惠券可以用？",
                "我要退货，订单2的商品有问题",
                "你们的服务太差了！我要投诉！",
                "你好呀",
            ],
            inputs=msg_input,
        )

        gr.Markdown(
            "---\n"
            "💡 **功能说明**：\n"
            "- 🔍 **售前咨询**：产品推荐、购买建议\n"
            "- 📋 **产品问答**：规格参数、使用方法\n"
            "- 📦 **订单查询**：订单状态、物流追踪\n"
            "- 🎫 **优惠券**：查询优惠、验证优惠码\n"
            "- 🔧 **售后服务**：退款、换货、维修\n"
            "- 👤 **人工转接**：复杂问题转人工\n"
            "- 😊 **情感识别**：自动识别用户情绪"
        )

    demo.launch(
        server_name=config.gradio_server_name,
        server_port=config.gradio_server_port,
    )


if __name__ == "__main__":
    main()

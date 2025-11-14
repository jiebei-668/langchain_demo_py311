import time

from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from demo01.tools import rag, construct_kg
import gradio as gr
from demo01.config.config import Config

cnotallow = {"configurable": {"thread_id": "user_1"}}

# 对于任何提供 OpenAI 兼容 API 的模型
model = ChatOpenAI(
        model="glm-4",  # 实际模型名称
        base_url="https://open.bigmodel.cn/api/paas/v4/",  # API 地址
        api_key="f1c06ff516bb472eb265b503934e57f0.Zn9g6lMZyrWS43FT",  # API 密钥
        temperature=0.1,
        max_tokens=1000,
        timeout=30
)
agent = create_agent(model, tools=[rag, construct_kg])


# 第一个参数和第二个参数一个是历史，一个是当前信息，貌似和gr.Textbox().submit第二个参数顺序有关
def chat_with_agent(message, chat_history):
    format_msg = {"role": "user", "content": message}
    chat_history.append(format_msg)
    # messages = [{"role": "user", "content": message}]
    result = agent.invoke({"messages": chat_history}, cnotallow={"configurable": {"thread_id": "user_1"}})

    # 提取Agent的回复
    if hasattr(result, 'get') and 'output' in result:
        response = result['output']
    else:
        response = {"role": "assistant", "content": str(result)}

        # 更新聊天历史
        chat_history.append(response)

        return "", chat_history



# 流式产生内容
def create_stream_output(history: list):
    response = history[-1]["content"]
    history.pop()
    template = {"role": "assistant", "content": ""}
    history.append(template)
    for character in response:
        history[-1]["content"] += character
        time.sleep(0.05)

        yield history


def main():
    with gr.Blocks() as demo:
        with gr.Tab("待扩展"):
            gr.Textbox(label="待扩展")
        with gr.Tab("YWAent"):
            gr.Markdown("我是运维专家，你可以问我相关的问题！")

            chatbot = gr.Chatbot(elem_id="chatbot", bubble_full_width=False, type="messages")

            # chat_input = gr.MultimodalTextbox(
            #     interactive=True,
            #     file_count="multiple",
            #     placeholder="请输入或者上传文件",
            #     show_label=False,
            #     sources=["microphone", "upload"],
            # )

            chat_input = gr.Textbox("请和我对话。。。")

            chat_msg = chat_input.submit(
                chat_with_agent, [chat_input, chatbot], [chat_input, chatbot]
            )
            bot_msg = chat_msg.then(create_stream_output, chatbot, chatbot, api_name="bot_response")
            # bot_msg.then(lambda: gr.MultimodalTextbox(interactive=True), None, [chat_input])
            bot_msg.then(lambda: gr.Textbox(interactive=True), None, [chat_input])


    demo.launch(
        server_name="0.0.0.0"
        , server_port=int(Config.get_instance().get_with_nested_params("server", "ui_port"))
        , share=Config.get_instance().get_with_nested_params("server", "ui_share")
        , max_threads=10
    )


if __name__ == '__main__':
    main()
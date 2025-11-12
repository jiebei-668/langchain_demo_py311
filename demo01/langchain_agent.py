
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

# while True:
#     user_input = input()
#     # response = agent.invoke({"message": [{"role": "user", "content": "hello"}]})
#     # NOTE: 没有cnotallow不能跑
#     result1 = agent.invoke({"messages": [{"role": "user", "content": user_input}]},
#                                cnotallow={"configurable": {"thread_id": "user_1"}})
#     print(result1)


def chat_with_agent(message, chat_history):
    messages = [{"role": "user", "content": message}]
    result = agent.invoke({"messages": messages}, cnotallow={"configurable": {"thread_id": "user_1"}})

    # 提取Agent的回复
    if hasattr(result, 'get') and 'output' in result:
        response = result['output']
    else:
        response = str(result)

        # 更新聊天历史
        chat_history.append((message, response))

        return response

def yes_man(message, history):
    if message.endswith("?"):
        return "Yes"
    else:
        return "Ask me anything!"


def run_webui():
    chat_app = gr.ChatInterface(
        chat_with_agent,
        chatbot=gr.Chatbot(height=400),
        textbox=gr.Textbox(placeholder="请输入你的问题", container=False, scale=7),
        title="YWAgent",
        description="你可以问关于运维的问题",
        theme="default",
        examples=["根据文档库总结西游记主要内容",
                  "请根据所给文字来构建知识图谱，文字为：李明是张华的表哥，而王芳则是他们共同的大学同学。"],
        cache_examples=False,
        submit_btn="发送",
        stop_btn="停止",
    )

    chat_app.launch(server_name="0.0.0.0"
                    , server_port=int(Config.get_instance().get_with_nested_params("server", "ui_port"))
                    , share=Config.get_instance().get_with_nested_params("server", "ui_share")
                    , max_threads=10)

if __name__ == '__main__':
    run_webui()
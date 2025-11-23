import time

from langchain_core.messages import AIMessage, ToolMessage
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from demo01.tools import rag, construct_kg, llm_dialogue_tool, get_solution_by_task_name

from demo01.config.config import Config

from typing import Dict, Any
import gradio as gr
import json
import tempfile
import webbrowser
from pathlib import Path
from demo01_env import get_env_value

cnotallow = {"configurable": {"thread_id": "user_1"}}

# 对于任何提供 OpenAI 兼容 API 的模型
model = ChatOpenAI(
        model=get_env_value("MODEL_NAME"),  # 实际模型名称
        base_url=get_env_value("LLM_BASE_URL"),  # API 地址
        api_key=get_env_value("LLM_API_KEY"),  # API 密钥
        temperature=0.1,
        max_tokens=1000,
        timeout=30
)
agent = create_agent(model, tools=[rag, construct_kg, get_solution_by_task_name])


# 第一个参数和第二个参数一个是历史，一个是当前信息，貌似和gr.Textbox().submit第二个参数顺序有关
def chat_with_agent(message, chat_history):
    format_msg = {"role": "user", "content": message}
    chat_history.append(format_msg)
    # messages = [{"role": "user", "content": message}]
    result = agent.invoke({"messages": chat_history}, cnotallow={"configurable": {"thread_id": "user_1"}})



    # 提取agent的回答
    if isinstance(result["messages"][-2], ToolMessage):
        response = result["messages"][-2].content
    else:
        response = result["messages"][-1].content

    # 更新聊天历史
    chat_history.append({"content": response, "role": "assistant"})

    return "", chat_history



# 流式产生内容
def create_stream_output(history: list):
    if history == []:
        return []
    response = history[-1]["content"]
    history.pop()
    template = {"role": "assistant", "content": ""}
    history.append(template)
    for character in response:
        history[-1]["content"] += character
        time.sleep(0.05)

        yield history


def generate_graph_html(graph_data: Dict[str, Any]) -> str:
    """生成包含图形可视化功能的HTML"""

    html_template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Knowledge Graph Visualization</title>
        <script src="https://unpkg.com/cytoscape/dist/cytoscape.min.js"></script>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }}

            body {{
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                min-height: 100vh;
                padding: 20px;
            }}

            .container {{
                max-width: 1200px;
                margin: 0 auto;
                background-color: white;
                border-radius: 12px;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
                overflow: hidden;
            }}

            header {{
                background: linear-gradient(90deg, #4b6cb7 0%, #182848 100%);
                color: white;
                padding: 20px 30px;
                text-align: center;
            }}

            h1 {{
                font-size: 28px;
                font-weight: 600;
                margin-bottom: 10px;
            }}

            #cy {{
                width: 100%;
                height: 600px;
                background-color: #fafafa;
                border: 1px solid #e0e0e0;
            }}

            .controls {{
                padding: 15px 20px;
                background-color: #f8f9fa;
                border-top: 1px solid #e0e0e0;
                display: flex;
                gap: 10px;
                justify-content: center;
            }}

            button {{
                padding: 8px 16px;
                background-color: #4b6cb7;
                color: white;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-size: 14px;
                transition: background-color 0.2s;
            }}

            button:hover {{
                background-color: #3a5999;
            }}

            footer {{
                padding: 15px 30px;
                text-align: center;
                color: #6c757d;
                font-size: 14px;
                border-top: 1px solid #e0e0e0;
                background-color: #f8f9fa;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>Knowledge Graph Visualization</h1>
                <p>Interactive graph display powered by Cytoscape.js</p>
            </header>

            <div id="cy"></div>

            <div class="controls">
                <button onclick="applyLayout('cose')">Force-Directed Layout</button>
                <button onclick="applyLayout('grid')">Grid Layout</button>
                <button onclick="applyLayout('circle')">Circular Layout</button>
                <button onclick="fitGraph()">Fit to Screen</button>
            </div>

            <footer>
                <p>Graph Visualization Tool | Click and drag to interact with nodes</p>
            </footer>
        </div>

        <script>
            // 初始化Cytoscape
            const cy = cytoscape({{
                container: document.getElementById('cy'),
                elements: {json.dumps(graph_data)},
                style: [
                    {{
                        selector: 'node',
                        style: {{
                            'background-color': 'data(color)',
                            'label': 'data(label)',
                            'color': '#000',
                            'text-valign': 'center',
                            'text-halign': 'center',
                            'font-size': '14px',
                            'width': 'label',
                            'height': 'label',
                            'padding': '10px',
                            'border-width': '2px',
                            'border-color': '#fff'
                        }}
                    }},
                    {{
                        selector: 'edge',
                        style: {{
                            'width': 3,
                            'line-color': 'data(color)',
                            'target-arrow-color': 'data(color)',
                            'curve-style': 'bezier',
                            'target-arrow-shape': 'triangle',
                            'label': 'data(label)',
                            'font-size': '12px'
                        }}
                    }}
                ],
                layout: {{
                    name: 'cose',
                    fit: true,
                    animate: true,
                    animationDuration: 1000
                }}
            }});

            // 布局函数
            function applyLayout(layoutName) {{
                const layoutOptions = {{
                    name: layoutName,
                    fit: true,
                    animate: true,
                    animationDuration: 800
                }};

                if (layoutName === 'grid') {{
                    layoutOptions.rows = Math.ceil(Math.sqrt(cy.nodes().length));
                }}

                cy.layout(layoutOptions).run();
            }}

            function fitGraph() {{
                cy.fit();
                cy.center();
            }}

            // 添加交互功能
            cy.on('tap', 'node', function(evt) {{
                const node = evt.target;
                cy.animate({{
                    fit: {{
                        eles: node,
                        padding: 50
                    }},
                    duration: 500
                }});
            }});

            cy.on('tap', function(evt) {{
                if (evt.target === cy) {{
                    cy.animate({{
                        fit: {{
                            eles: cy.elements(),
                            padding: 50
                        }},
                        duration: 500
                    }});
                }}
            }});
        </script>
    </body>
    </html>
    """
    return html_template


def create_graph_html_file(graph_data: Dict[str, Any]) -> str:
    """创建HTML文件并返回文件路径"""
    html_content = generate_graph_html(graph_data)

    # 创建临时文件，在/tmp目录下生成随机名的目录，比如有一次是/tmp/tmpuey9oabb/
    temp_dir = tempfile.mkdtemp()
    html_file = Path(temp_dir) / "graph_visualization.html"

    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

    return str(html_file)
from demo01.prompts.kg_construct import __retriever_prompt

def open_graph_in_browser(text_input: str):
    """在新窗口中打开图形可视化"""
    messages = [
        {"role": "system", "content": "你现在扮演信息抽取的角色，要求根据用户输入和AI的回答，正确提取出信息。"},
        {"role": "user", "content": text_input},
        {"role": "user", "content": __retriever_prompt}
    ]
    result = llm_dialogue_tool(messages)
    graph_data = json.loads(result)

    html_file = create_graph_html_file(graph_data)
    webbrowser.open(f"file://{html_file}")

    return f"Graph visualization opened in new window: {html_file}"

def extract_entities_and_relations(text: str) -> Dict[str, Any]:
    """从文本中提取实体和关系（简化版本）"""
    # 这里可以实现更复杂的NLP处理
    # 目前使用简单的基于规则的提取

    nodes = []
    edges = []
    node_id = 1
    edge_id = 1

    # 简单的实体提取（实际应用中可以使用spaCy等库）
    words = text.split()
    entities = [word for word in words if len(word) > 3 and word[0].isupper()]

    for i, entity in enumerate(set(entities)):  # 去重
        nodes.append({
            "data": {
                "id": str(node_id),
                "label": entity,
                "color": get_color(i)
            }
        })
        node_id += 1

    # 简单的关系提取
    if len(nodes) > 1:
        for i in range(len(nodes) - 1):
            edges.append({
                "data": {
                    "id": f"e{edge_id}",
                    "source": nodes[i]["data"]["id"],
                    "target": nodes[i + 1]["data"]["id"],
                    "label": "related to",
                    "color": get_color(i + len(nodes))
                }
            })
            edge_id += 1

    return {"nodes": nodes, "edges": edges}


def get_color(index: int) -> str:
    """获取颜色"""
    colors = [
        "#FFB3BA", "#FFDFBA", "#FFFFBA", "#BAFFC9", "#BAE1FF",
        "#B5EAD7", "#ECC5FB", "#FFC3A0", "#FF9AA2", "#FFDAC1"
    ]
    return colors[index % len(colors)]


def main():
    with gr.Blocks() as demo:
        with gr.Tab("YWAgent"):
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
        with gr.Tab("自动构建知识图谱"):
            gr.Markdown("# 图谱构建&可视化")

            with gr.Row():
                text_input = gr.Textbox(
                    label="请输入用以构建图谱的原文",
                    lines=10,
                    # value=json.dumps(EXAMPLE_DATA, indent=2)
                )

            with gr.Row():
                submit_btn = gr.Button("构建并在新窗口可视化", variant="primary")
                status = gr.Textbox(label="状态", interactive=False)

            submit_btn.click(
                fn=open_graph_in_browser,
                inputs=text_input,
                outputs=status
            )



    demo.launch(
        server_name="0.0.0.0"
        , server_port=int(Config.get_instance().get_with_nested_params("server", "ui_port"))
        , share=Config.get_instance().get_with_nested_params("server", "ui_share")
        , max_threads=10
    )


if __name__ == '__main__':
    main()
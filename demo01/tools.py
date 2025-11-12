from typing import Tuple

from langchain.tools import tool
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from demo01.dao.graph.graph_dao import GraphDao
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain_community.vectorstores import FAISS
from langchain_openai.chat_models import ChatOpenAI
from demo01.model.rag.retriever_service import retrieve



_dao = GraphDao()

@tool
def search(query: str) -> str:
    """Search for information."""
    return f"Results for: {query}"

@tool
def get_weather(location: str) -> str:
    """Get weather information for a location."""
    return f"Weather in {location}: Sunny, 72°F"



@tool
def get_solution_by_task_name(task_name) -> Tuple[list, str]:
    """根据任务名称查询系统问题的解决方案步骤。

    这个工具用于处理系统相关问题，如系统重装、故障排查等。
    输入任务名称，返回详细的解决步骤列表和执行结果。"""
    steps =_dao.query_task_steps_ordered_list(task_name)
    # fixme 这里补充自动执行的结果
    return steps, '执行成功'





@tool
def rag(query: str) -> str:
    """该工具接收用户查询，根据文档库中的知识回答用户问题"""

    docs = retrieve(query, 3)


    # 格式化上下文信息
    context = "\n\n".join([f"文档片段 {i + 1}:\n{doc.page_content}" for i, doc in enumerate(docs)])
    # return docs, context
    # 构建包含检索上下文的用户消息
    rag_user_message = f"""
        基于以下上下文信息回答问题：\n上下文：\n{context}\n问题：\n{query}\n\n
        请仅使用上述上下文中的信息回答问题，
        如果上下文没有相关信息，直接说明"没有找到相关信息"。
    """

    # 构建消息列表
    messages = [{"role": "user", "content": rag_user_message}]

    response = llm_dialogue_tool(messages)
    return response


# 定义调用LLM的Tool
def llm_dialogue_tool(query: str) -> str:
    """用于直接与LLM对话的工具"""
    llm = ChatOpenAI(model="glm-4", base_url="https://open.bigmodel.cn/api/paas/v4/", api_key="f1c06ff516bb472eb265b503934e57f0.Zn9g6lMZyrWS43FT")
    response = llm.invoke(query)
    return response.content

@tool
def construct_kg(raw_text: str):
    """使用LLM从原始文本中抽取实体和关系然后构建知识图谱/知识图谱三元组"""
    from demo01.prompts.kg_construct import __retriever_prompt
    messages = [
        {"role": "system", "content": "你现在扮演信息抽取的角色，要求根据用户输入和AI的回答，正确提取出信息。"},
        {"role": "user", "content": raw_text},
        {"role": "user", "content": __retriever_prompt}
    ]
    result = llm_dialogue_tool(messages)
    return result

if __name__ == '__main__':
    from langchain_openai import ChatOpenAI
    from langchain.agents import create_agent
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
    agent = create_agent(model, tools=[search, get_weather, get_solution_by_task_name, rag, construct_kg])

    while True:
        user_input = input()
        # response = agent.invoke({"message": [{"role": "user", "content": "hello"}]})
        # NOTE: 没有cnotallow不能跑
        result1 = agent.invoke({"messages": [{"role": "user", "content": user_input}]},
                               cnotallow={"configurable": {"thread_id": "user_1"}})
        print(result1)



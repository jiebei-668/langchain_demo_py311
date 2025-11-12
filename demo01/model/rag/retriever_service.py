
from typing import List, Any

from langchain_core.documents import Document

from demo01.model.rag.rag import INSTANCE


def retrieve(query: str, top_k) -> List[Document]:

    docs = INSTANCE.vector.similarity_search(query, k=top_k)

    return docs


def search(query: str, search_type: str, **kwargs: Any) -> List[Document]:
    docs = INSTANCE.vector_db.search(query, search_type, **kwargs)
    return docs

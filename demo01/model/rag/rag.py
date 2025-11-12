import os

from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings

from demo01.demo01_env import get_app_root
from demo01.model.embedding.huggingface_embedding import HuggingfaceEmbedding
class Rager:
    _embedding = HuggingfaceEmbedding().embedding
    _doc_data_path = os.path.join(get_app_root(), "docs")
    _name = "rag_retriever"
    _model_path_base = os.path.join(get_app_root(), f"data/model/{_name}")
    _topK = 3



    def __init__(self):
        self._version = 1
        self._vector = None
        self._retriever = None

    # 构建向量库
    def build(self, *args, **kwargs):

        # self._version = self.get_latest_model_version() + 1
        # self._logger.info(f"building version {self._version}")

        loader = DirectoryLoader(
            path=Rager._doc_data_path,
            glob="*.txt",
            loader_cls=TextLoader,
            loader_kwargs={"encoding": "utf-8"}
        )
        docs = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100,
            separators=["\n\n", "\n", " ", ""]
        )
        documents = text_splitter.split_documents(docs)
        self._vector = FAISS.from_documents(documents, self._embedding)

        # fixme 这个暂时没用
        self._retriever = self._vector.as_retriever(search_kwargs={"k": 6})


        self.dump(**kwargs)

    # 把向量持久化以及存储模型版本信息
    def dump(self, *args, **kwargs):
        # fixme 这里可以存储一些版本信息
        self._dump_model()

    # 仅将向量持久化
    def _dump_model(self):
        model_path = self.get_model_path(version=self._version, create=True)
        self._vector.save_local(model_path)

    def get_model_path(self, version: int, create: bool = False):
        if not os.path.exists(self._model_path_base):
            os.makedirs(self._model_path_base)

        path_ = os.path.join(self._model_path_base, str(version), "model")
        dir_ = os.path.dirname(path_)

        if not os.path.exists(dir_) and create:
            os.makedirs(dir_)

        return path_

    @property
    def retriever(self):
        if self._retriever is None:
            self.build()
        return self._retriever

    @property
    def vector(self):
        if self._vector is None:
            self.build()
        return self._vector

INSTANCE = Rager()


def initialize_vector_store(embedding_model: str, docs_dir: str, persist_dir: str = "vector_db") -> FAISS:
    global vector_store
    # load and chunk document
    # 从docs目录中获取所有txt文件
    loader = DirectoryLoader(
        docs_dir,
        glob="*.txt",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"}
    )
    documents = loader.load()
    # split
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
        separators=["\n\n", "\n", " ", ""]
    )
    splits = text_splitter.split_documents(documents)
    # embeddings
    # embeddings 模型是all-MiniLM-L6-v2
    embeddings = HuggingFaceEmbeddings(model_name=embedding_model)
    # 持久化存储
    vector_store = FAISS.from_documents(splits, embeddings)
    vector_store.save_local(persist_dir)
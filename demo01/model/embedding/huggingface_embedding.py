
from langchain_community.embeddings import HuggingFaceEmbeddings

from demo01.config.config import Config


class HuggingfaceEmbedding:

    def __init__(self, model_name_or_path=None, device=None, **kwargs):
        super().__init__(**kwargs)
        self._vector_db = None
        if not model_name_or_path:
            model_name_or_path = Config.get_instance().get_with_nested_params("model", "embedding", "model-name")
        self._embedding = HuggingFaceEmbeddings(model_name=model_name_or_path,

                                               )

        if device:
            self._device = device
        else:
            self._device = Config.get_instance().get_with_nested_params("model", "embedding", "device")

    @property
    def embedding(self):
        return self._embedding

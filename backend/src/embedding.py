from config import config
from pymilvus.model.dense import JinaEmbeddingFunction

class WrappedJinaEmbeddingFunction(JinaEmbeddingFunction):
    def embed_documents(self, texts: list[str]) -> list:
        """
        Returns embeddings for a list of document texts by calling the underlying
        encode_documents method.
        """
        return self.encode_documents(texts)
    
    def embed_query(self, text: str) -> list[float]:
        """
        Returns an embedding for a single query by calling the underlying
        encode_queries method.
        """
        # encode_queries expects a list of queries, so we wrap the input in a list
        # and return the first (and only) embedding.
        return self.encode_queries([text])[0]

def get_embedding_function():
    return WrappedJinaEmbeddingFunction(
        model_name=config.JINA_MODEL_NAME,
        api_key=config.JINAAI_API_KEY,
        task=config.JINA_TASK,
        dimensions=config.JINA_DIM,
    )
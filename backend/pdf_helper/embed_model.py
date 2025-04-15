import httpx
import numpy as np

class OllamaEmbeddingWrapper:
    def __init__(self, api_url: str = "http://localhost:11434/api/embed", 
                 model: str = "EntropyYue/jina-embeddings-v2-base-zh"):
        self.api_url = api_url
        self.model = model

    def encode(self, texts, batch_size: int = 1) -> np.ndarray:
        """
        Mimics SentenceTransformer.encode().
        Accepts a single string or a list of strings and returns a numpy array
        with the embedding(s) obtained from the Ollama /api/embed endpoint.
        """
        # Normalize to a list if a single string is provided.
        if isinstance(texts, str):
            texts = [texts]
        
        payload = {
            "model": self.model,
            "input": texts  # The API accepts a string or a list under "input"
        }
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(self.api_url, json=payload)
                response.raise_for_status()
                data = response.json()
                # First try "embedding", then fall back to "embeddings".
                embedding = data.get("embedding")
                if embedding is None:
                    embedding = data.get("embeddings")
                    if embedding is None:
                        raise Exception(f"Missing 'embedding' key in response: {data}")
                # Return a numpy array (assuming a list or list of lists structure)
                return np.array(embedding)
        except Exception as e:
            raise Exception(f"Failed to fetch embedding from Ollama: {e}")

def get_embedding_model():
    """
    Returns an instance of the OllamaEmbeddingWrapper which generates embeddings by calling
    the Ollama /api/embed endpoint.
    """
    return OllamaEmbeddingWrapper()

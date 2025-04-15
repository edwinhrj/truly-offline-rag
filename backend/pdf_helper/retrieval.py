import numpy as np
from .embed_model import get_embedding_model
from .store import get_db_connection

def get_query_embedding(query: str) -> np.ndarray:
    """
    Encode the user's query into an embedding using the Ollama model via our wrapper.
    """
    model = get_embedding_model()
    return model.encode(query).astype(np.float32)

def retrieve_relevant_chunks(query_embedding: np.ndarray, limit: int = 3):
    """
    Connects to the SQLite database and retrieves the top document chunks most similar
    to the query embedding using the cosine distance function 'vec_distance_cosine'.
    """
    db, _ = get_db_connection()
    sql = """
        SELECT id, text, source, page, vec_distance_cosine(embedding, ?) AS distance
        FROM vec_items
        ORDER BY distance ASC
        LIMIT ?
    """
    cursor = db.execute(sql, (query_embedding.tobytes(), limit))
    rows = cursor.fetchall()
    db.close()
    return rows

def build_contextual_prompt(user_query: str, chunks) -> str:
    """
    Constructs an augmented prompt by including the retrieved document context and the user query.
    """
    context_lines = []
    for row in chunks:
        doc_id, text, source, page, distance = row
        context_lines.append(f"Source: {source}, Page: {page}:\n{text}")
    context = "\n\n".join(context_lines) if context_lines else "No relevant context found."
    prompt = f"""### System Instruction:
You are Deepseek-R1, a helpful AI assistant. Use the following context to answer the user's query as accurately as possible.

### Retrieved Context:
{context}

### Current Conversation:
User: {user_query}

### Assistant Response:
"""
    return prompt
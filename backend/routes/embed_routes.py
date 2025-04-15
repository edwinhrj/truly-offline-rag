# backend/routes/embed_routes.py
from flask import Blueprint, jsonify, request
import httpx
from ..pdf_helper.embed_model import get_embedding_model

embed_routes = Blueprint("embed_routes", __name__)

@embed_routes.route("/api/embed", methods=["POST"])
def embed_api():
    """
    Endpoint for computing text embeddings using the Ollama-based wrapper.
    Expects a JSON payload with a "text" field.
    """
    data = request.get_json()
    text = data.get("text", "")
    if not text:
        return jsonify({"error": "No text provided"}), 400
    try:
        model = get_embedding_model()
        embedding = model.encode(text)
        return jsonify({"embedding": embedding.tolist()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

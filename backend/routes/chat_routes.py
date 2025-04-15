# backend/routes/chat_routes.py
from flask import Blueprint, jsonify, request, Response
import json, httpx
from ..ollama.ollama_manager import OllamaManager
from ..pdf_helper.retrieval import get_query_embedding, retrieve_relevant_chunks, build_contextual_prompt

chat_routes = Blueprint("chat_routes", __name__)

@chat_routes.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_query = data.get('message', '')
    if not user_query:
        return jsonify({"error": "No query provided."}), 400

    # Retrieve context by computing the query embedding and performing the search.
    query_embedding = get_query_embedding(user_query)
    chunks = retrieve_relevant_chunks(query_embedding, limit=3)
    prompt = build_contextual_prompt(user_query, chunks)

    manager = OllamaManager()
    if not manager.is_model_installed():
        return jsonify({"error": "Model not installed. Please complete setup first."}), 400

    def generate():
        payload = {
            "model": "deepseek-r1:1.5b",
            "prompt": prompt,
            "stream": True
        }
        try:
            with httpx.Client(timeout=60.0) as client:
                with client.stream("POST", "http://localhost:11434/api/generate", json=payload) as response:
                    if response.status_code != 200:
                        error_detail = response.text
                        yield f"Error: Received status {response.status_code}. Details: {error_detail}"
                        return
                    for chunk in response.iter_lines():
                        try:
                            decoded_chunk = chunk.decode("utf-8") if isinstance(chunk, bytes) else chunk
                            data_chunk = json.loads(decoded_chunk)
                            if "response" in data_chunk:
                                yield data_chunk["response"]
                            if data_chunk.get("done", False):
                                break
                        except json.JSONDecodeError:
                            continue
        except httpx.ConnectError:
            yield "Error: Could not connect to Ollama server. Is it running?"
        except Exception as e:
            yield f"Error: {str(e)}"

    return Response(generate(), mimetype='text/plain')

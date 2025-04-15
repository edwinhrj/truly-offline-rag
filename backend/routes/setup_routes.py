# backend/routes/setup_routes.py
import threading
from flask import Blueprint, jsonify
from ..ollama.ollama_manager import OllamaManager
from ..ollama.models_config import MODELS

setup_routes = Blueprint("setup_routes", __name__)

# Global progress storage for the setup task.
setup_progress = {"stage": None, "progress": 0, "error": None}

def run_setup_task():
    manager = OllamaManager()

    def progress_callback(stage, progress=None):
        setup_progress["stage"] = stage
        setup_progress["progress"] = progress

    try:
        manager.setup_ollama(progress_callback)
    except Exception as e:
        setup_progress["error"] = str(e)
        print(f"Setup error: {e}")

@setup_routes.route("/api/setup", methods=["POST"])
def setup():
    # Run setup in a separate thread so the request returns immediately.
    thread = threading.Thread(target=run_setup_task, daemon=True)
    thread.start()
    return jsonify({"success": True, "message": "Setup started successfully"})

@setup_routes.route("/api/status", methods=["GET"])
def status():
    manager = OllamaManager()
    models_installed = {model: manager.is_model_installed(model) for model in MODELS}
    return jsonify({
        "ollamaInstalled": manager.is_ollama_installed(),
        "ollamaRunning": manager.is_ollama_running(),
        "modelsInstalled": models_installed,
        "progress": setup_progress,
        "error": setup_progress.get("error")
    })

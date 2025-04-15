from flask import Blueprint, send_from_directory
from pathlib import Path

general_routes = Blueprint("general_routes", __name__)

@general_routes.route('/', defaults={'path': ''})
@general_routes.route('/<path:path>')
def serve_static(path):
    # Resolve the absolute path to the 'frontend/dist' folder.
    frontend_path = Path(__file__).parent.parent.parent / "frontend" / "dist"
    file_path = frontend_path / path
    
    # If no path is given or file doesn't exist, serve index.html.
    if not path or not file_path.exists() or file_path.is_dir():
        return send_from_directory(frontend_path, "index.html")
    
    return send_from_directory(frontend_path, path)
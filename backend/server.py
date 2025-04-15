# backend/server.py
from flask import Flask
from flask_cors import CORS
from pathlib import Path
from .pdf_helper.store import initialize_database

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# Initialize the SQLite database (creates the vec_items table if needed).
initialize_database()

# Register the blueprint for SQLite upload routes.
from .routes.sqlite_routes import sqlite_bp
app.register_blueprint(sqlite_bp, url_prefix="/sqlite")

# Register all other route blueprints.
from .routes.setup_routes import setup_routes
from .routes.embed_routes import embed_routes
from .routes.chat_routes import chat_routes
from .routes.general_routes import general_routes

app.register_blueprint(setup_routes)      # Contains /api/setup and /api/status endpoints.
app.register_blueprint(embed_routes)      # Contains /api/embed endpoint.
app.register_blueprint(chat_routes)       # Contains /api/chat endpoint.
app.register_blueprint(general_routes)    # Contains /health and static file serving endpoints.

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080)

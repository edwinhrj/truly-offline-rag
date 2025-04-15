# backend/routes/sqlite_routes.py
import tempfile
import os
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from ..pdf_helper.parse import load_documents, calculate_chunk_ids, split_documents
from ..pdf_helper.store import add_to_sqlite, clear_sqlite_database

sqlite_bp = Blueprint('sqlite', __name__)

@sqlite_bp.route('/upload', methods=['POST'])
def upload_pdf():
    """Handle PDF file upload, process it, and store in SQLite."""
    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"status": "error", "message": "No selected file"}), 400
    if not file.filename.lower().endswith('.pdf'):
        return jsonify({"status": "error", "message": "File must be a PDF"}), 400
    try:
        original_filename = secure_filename(file.filename)
        temp_file_name = os.path.join(tempfile.gettempdir(), original_filename)
        file.save(temp_file_name)
        print(f"Saved uploaded file to: {temp_file_name}")
    except Exception as e:
        return jsonify({"status": "error", "message": f"Failed to upload file: {str(e)}"}), 500
    try:
        documents = load_documents(temp_file_name)
        chunks = split_documents(documents)
        chunks = calculate_chunk_ids(chunks)
        add_to_sqlite(chunks)
        return jsonify({"status": "success", "message": f"Successfully processed PDF: {original_filename}"})
    except Exception as e:
        return jsonify({"status": "error", "message": f"Failed to process file: {str(e)}"}), 500
    finally:
        if os.path.exists(temp_file_name):
            os.remove(temp_file_name)

@sqlite_bp.route('/clear', methods=['POST'])
def clear_database():
    try:
        clear_sqlite_database()
        return jsonify({"status": "success", "message": "Database cleared successfully"})
    except Exception as e:
        return jsonify({"status": "error", "message": f"Failed to clear database: {str(e)}"}), 500

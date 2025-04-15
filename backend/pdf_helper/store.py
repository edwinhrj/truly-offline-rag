import sqlite3
import numpy as np
from pathlib import Path
from langchain.schema.document import Document
from .embed_model import get_embedding_model
from .parse import calculate_chunk_ids
import sys

if getattr(sys, 'frozen', False):
    base = Path(sys._MEIPASS)
    print("sys._MEIPASS is located at:", base)
    for item in base.rglob("*"):
        print(item.relative_to(base))
else:
    print("Application is not frozen; not using sys._MEIPASS.")

def get_db_connection():
    home_dir = Path.home()
    app_data_dir = home_dir / ".mandiao"
    app_data_dir.mkdir(exist_ok=True)
    db_path = app_data_dir / "mandiao.db"
    db = sqlite3.connect(str(db_path))
    db.enable_load_extension(True)
   
    try:
        if getattr(sys, 'frozen', False):
            ext_path = Path(sys._MEIPASS) / "backend" / "pdf_helper"
        else:
            ext_path = Path(__file__).parent
        extension_file = ext_path / "vec0.dll"  # Adjust filename if needed.
        print("Attempting to load sqlite-vec extension from:", extension_file)
        
        if not extension_file.exists():
            raise FileNotFoundError(f"{extension_file} does not exist.")
        
        db.load_extension(str(extension_file))
        print("sqlite-vec extension loaded successfully.")
    except Exception as e:
        print("Failed to load sqlite-vec extension:", e)
    finally:
        db.enable_load_extension(False)
    return db, db_path

def initialize_database():
    """
    Initializes the SQLite database by creating the vec_items table if it does not exist.
    This ensures that the chat endpoint does not error out on first run.
    """
    db, _ = get_db_connection()
    try:
        db.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS vec_items 
            USING vec0(id TEXT, text TEXT, source TEXT, page INTEGER, embedding float[768] distance_metric=cosine)
        """)
        db.commit()
        print("Database initialization completed.")
    except Exception as e:
        print("Database initialization error:", e)
    finally:
        db.close()

def clear_sqlite_database():
    db, _ = get_db_connection()
    try:
        db.execute("DROP TABLE IF EXISTS vec_items")
        db.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS vec_items 
            USING vec0(id TEXT, text TEXT, source TEXT, page INTEGER, embedding float[768] distance_metric=cosine)
        """)
        db.commit()
        return True
    except Exception as e:
        print(f"Error clearing database: {e}")
        raise
    finally:
        db.close()

def add_to_sqlite(chunks: list[Document]):
    db, _ = get_db_connection()
    db.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS vec_items 
        USING vec0(id TEXT, text TEXT, source TEXT, page INTEGER, embedding float[768] distance_metric=cosine)
    """)
    existing_items = db.execute("SELECT id FROM vec_items").fetchall()
    existing_ids = {item[0] for item in existing_items}
    print(f"number of existing documents in db: {len(existing_ids)}")
    new_chunks = [chunk for chunk in chunks if chunk.metadata["id"] not in existing_ids]
    if new_chunks:
        print(f"adding new documents: {len(new_chunks)}")
        for chunk in new_chunks:
            chunk_text = chunk.page_content
            model = get_embedding_model()
            embedding = model.encode(chunk_text).astype(np.float32)
            db.execute(
                "INSERT INTO vec_items(id, text, source, page, embedding) VALUES (?, ?, ?, ?, ?)",
                [chunk.metadata["id"], chunk_text, chunk.metadata["source"], chunk.metadata["page"], embedding]
            )
        print("new documents added to sqlite db")
    else:
        print("no new documents to be added")
    db.commit()
    db.close()
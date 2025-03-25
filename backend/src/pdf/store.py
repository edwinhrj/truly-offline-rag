import sqlite3
import sqlite_vec
import numpy as np
from langchain.schema.document import Document
from sentence_transformers import SentenceTransformer
from .parse import calculate_chunk_ids

def add_to_sqlite(chunks: list[Document]):
    db = sqlite3.connect('mandiao.db')
    db.enable_load_extension(True) 
    sqlite_vec.load(db)
    db.enable_load_extension(False)
    model = SentenceTransformer("src/pdf/model") # load pre installed embed model

    # create a vector table to store vectors, together with non-vector metadata
    db.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS vec_items 
        USING vec0(chunk_id TEXT, chunk_text TEXT, source TEXT, page INTEGER, embedding float[768] distance_metric=cosine)
        """)

    # retreive current chunk ids in sqlite db
    existing_items = db.execute("SELECT chunk_id FROM vec_items").fetchall()
    existing_ids = set([item[0] for item in existing_items])
    print(f"Number of existing documents in DB: {len(existing_ids)}")

    # only add documents that don't already exist in the db.
    new_chunks = []
    for chunk in chunks:
        if chunk.metadata["id"] not in existing_ids:
            new_chunks.append(chunk)

    if len(new_chunks):
        print(f"adding new documents: {len(new_chunks)}")
        for chunk in new_chunks:
            chunk_text = chunk.page_content # string
            embedding = model.encode(chunk_text).astype(np.float32)
            db.execute(
                "INSERT INTO vec_items(chunk_id, chunk_text, source, page, embedding) VALUES (?, ?, ?, ?, ?)",
                [chunk.metadata["id"], chunk_text, chunk.metadata["source"], chunk.metadata["page"], embedding],
            )
        print("new documents added to sqlite db")
    else:
        print("no new documents to be added")
    db.commit()
    db.close()
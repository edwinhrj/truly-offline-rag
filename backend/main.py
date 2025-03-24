from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import sqlite_vec
from sentence_transformers import SentenceTransformer
import struct
from typing import List

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # vue frontend running on this port
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],  
)

def serialize_f32(vector: List[float]) -> bytes:
    """serializes a list of floats into a compact "raw bytes" format"""
    return struct.pack("%sf" % len(vector), *vector)

@app.get("/create")
def create_sqlite():
    try:
        # these code chunks must always be together, it turns the db into 
        db = sqlite3.connect('mandiao.db')
        db.enable_load_extension(True) 
        sqlite_vec.load(db)
        db.enable_load_extension(False) 

        items = [
        (1, [0.1, 0.1, 0.1, 0.1]),
        (2, [0.2, 0.2, 0.2, 0.2]),
        (3, [0.3, 0.3, 0.3, 0.3]),
        (4, [0.4, 0.4, 0.4, 0.4]),
        (5, [0.5, 0.5, 0.5, 0.5]),
        ]

        db.execute("CREATE VIRTUAL TABLE IF NOT EXISTS vec_items USING vec0(embedding float[4])")
        with db:
            for item in items:
                db.execute(
                    "INSERT INTO vec_items(rowid, embedding) VALUES (?, ?)",
                    [item[0], serialize_f32(item[1])],
                )
    except Exception as e:
        return {"error:", str(e)}

@app.get("/sqlite")
def read_data():
    # set up sqlite db
    db = sqlite3.connect('mandiao.db')
    # allow loading of vectors
    db.enable_load_extension(True) 
    sqlite_vec.load(db)
    db.enable_load_extension(False) # turn off 
    query = [0.3, 0.3, 0.3, 0.3]
    rows = db.execute(
        """
        SELECT
            rowid,
            distance
        FROM vec_items
        WHERE embedding MATCH ?
        ORDER BY distance
        LIMIT 1
        """,
        [serialize_f32(query)],
    ).fetchall()
    return rows

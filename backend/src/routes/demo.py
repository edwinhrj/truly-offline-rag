import sqlite3
import sqlite_vec
import struct
from typing import List
from fastapi import APIRouter

router = APIRouter()

def serialize_f32(vector: List[float]) -> bytes:
    """serializes a list of floats into a compact "raw bytes" format"""
    return struct.pack("%sf" % len(vector), *vector)

@router.post("/create")
def create_sqlite():
    try:
        # these code chunks must always be together, it adds vector functionality into the selected db
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

@router.post("/sqlite")
def read_data():

    # these code chunks must always be together, it adds vector functionality into the selected db
    db = sqlite3.connect('mandiao.db')
    db.enable_load_extension(True) 
    sqlite_vec.load(db)
    db.enable_load_extension(False) 

    query = [0.3, 0.3, 0.3, 0.3]

    rows = db.execute( # k nearest neighbour search
        """
        SELECT
            rowid,
            distance
        FROM vec_items
        WHERE embedding MATCH ?
        ORDER BY distance
        LIMIT 3
        """,
        [serialize_f32(query)],
    ).fetchall()
    return rows
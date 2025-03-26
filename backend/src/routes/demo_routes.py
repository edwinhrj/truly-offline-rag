import sqlite3
import sqlite_vec
from sentence_transformers import SentenceTransformer
from fastapi import APIRouter
import numpy as np
from src.pdf.embed_model import embed_model

router = APIRouter()

model = SentenceTransformer('src/pdf/embed_model') # load pre installed membed model

@router.post("/sqlite")
def read_data():

    # these code chunks must always be together, it adds vector functionality into the selected db
    db = sqlite3.connect('mandiao.db')
    db.enable_load_extension(True) 
    sqlite_vec.load(db)
    db.enable_load_extension(False) 


    query = "mongodb and redis"
    embedding = embed_model.encode(query)
    embedding = embedding.astype(np.float32)

    rows = db.execute( # k nearest neighbour search
        """
        SELECT
            id,
            text
        FROM vec_items
        WHERE embedding MATCH ?
        ORDER BY distance
        LIMIT 1
        """,
        [embedding],
    ).fetchall()
    db.commit()
    db.close()
    return rows
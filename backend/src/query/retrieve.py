import sqlite3
import sqlite_vec
from ..pdf.embed_model import embed_model
import numpy as np

def retrieve_similar_sentences(query):

    # these code chunks must always be together, it adds vector functionality into the selected db
    db = sqlite3.connect('mandiao.db')
    db.enable_load_extension(True) 
    sqlite_vec.load(db)
    db.enable_load_extension(False) 

    embedding = embed_model.encode(query)
    embedding = embedding.astype(np.float32)

    rows = db.execute( # cosine similarity search (best for sentiment; if can find better searches do update here!)
        """
        SELECT
            text
        FROM vec_items
        WHERE embedding MATCH ?
        ORDER BY distance
        LIMIT 5
        """,
        [embedding],
    ).fetchall()
    db.commit()
    db.close()
    return rows
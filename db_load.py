import psycopg
from embedding import chunks, embeddings

DIM = embeddings.shape[1]

with psycopg.connect("host=localhost port=5432 dbname=modulhandbuch user=postgres password=mhbpass") as conn:
    with conn.cursor() as cur:
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
        cur.execute("DROP TABLE IF EXISTS chunks")
        cur.execute(f"""
            CREATE TABLE chunks (
                id integer PRIMARY KEY,
                modul text,
                page text,
                text text,
                table_text text,
                dokument text,
                fassung text,
                embedding vector({DIM})
            )
        """)
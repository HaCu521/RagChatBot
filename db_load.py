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
        for i, c in enumerate(chunks):
            vec = '[' + ','.join(str(x) for x in embeddings[i]) + ']'  #vektor als pgvector-text
            cur.execute(
                "INSERT INTO chunks (id, modul, page, text, table_text, dokument, fassung, embedding) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                (i, c['modul'], str(c['page']), c['text'], c['table_text'], c['dokument'], c['fassung'], vec)
            )
        conn.commit()

        print('fertig:', len(chunks), 'chunks geladen')
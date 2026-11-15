from sentence_transformers import SentenceTransformer
import numpy as np
import json
import os
import psycopg

with open('data/chunks.json', encoding='utf-8') as f:
    chunks = json.load(f)

# model = SentenceTransformer('intfloat/multilingual-e5-small')
model = SentenceTransformer('BAAI/bge-m3')

texts = ['passage: ' + c['modul'] +' ' + c['text'] + ' ' + c['table_text'] for c in chunks]

if os.path.exists('data/embeddings.npy'):
    embeddings = np.load('data/embeddings.npy')
else:
    embeddings = model.encode(texts, normalize_embeddings=True)
    np.save('data/embeddings.npy', embeddings)

# embeddings = model.encode(texts, normalize_embeddings=True)
# np.save('data/embeddings.npy', embeddings)

#score vergleicht die ähnlichkeit der frage zu chunk, arbeitet mit npy
# def search(question, k=3, dedup=True):
#     q = model.encode('query: ' + question, normalize_embeddings=True)
#     scores = embeddings @ q
#     found = []
#     result = []
#     for b in scores.argsort()[::-1]:
#         if not dedup or chunks[b]['modul'] not in found:
#             found.append(chunks[b]['modul'])
#             result.append(chunks[b])
#         if len(result) == k:
#             break
#     return result

conn_db = psycopg.connect("host=localhost port=5432 dbname=modulhandbuch user=postgres password=mhbpass")


def search_db(question,k=3,dedup=True):
    q = model.encode('query: ' + question, normalize_embeddings=True)
    q_db= '[' + ','.join(str(x) for x in q) + ']'
    with conn_db.cursor() as cur:
        cur.execute(
            "SELECT modul, page, text, table_text, dokument, fassung "
            "FROM chunks ORDER BY embedding <=> %s LIMIT %s",  # equal zu scores = embeddings @ q
            (q_db, k * 5)
        )
        rows = cur.fetchall()

    found, result = [], []
    for modul, page, text, table_text, dokument, fassung in rows:
        if not dedup or modul not in found:
            found.append(modul)
            result.append({'modul': modul, 'page': page, 'text': text,
                           'table_text': table_text, 'dokument': dokument, 'fassung': fassung})
        if len(result) == k:
            break
    return result



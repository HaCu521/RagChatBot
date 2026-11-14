from sentence_transformers import SentenceTransformer
import numpy as np
import json
import os

with open('data/chunks.json', encoding='utf-8') as f:
    chunks = json.load(f)

model = SentenceTransformer('intfloat/multilingual-e5-small')
# model = SentenceTransformer('BAAI/bge-m3') viel zu langsam

texts = ['passage: ' + c['modul'] +' ' + c['text'] + ' ' + c['table_text'] for c in chunks]

# if os.path.exists('data/embeddings.npy'):
#     embeddings = np.load('data/embeddings.npy')
# else:
#     embeddings = model.encode(texts, normalize_embeddings=True)
#     np.save('data/embeddings.npy', embeddings)

embeddings = model.encode(texts, normalize_embeddings=True)
np.save('data/embeddings.npy', embeddings)

#score vergleicht die ähnlichkeit der frage zu chunk
def search(question, k=3, dedup=True):
    q = model.encode('query: ' + question, normalize_embeddings=True)
    scores = embeddings @ q
    found = []
    result = []
    for b in scores.argsort()[::-1]:
        if not dedup or chunks[b]['modul'] not in found:
            found.append(chunks[b]['modul'])
            result.append(chunks[b])
        if len(result) == k:
            break
    return result


from sentence_transformers import SentenceTransformer
import numpy as np
import json

with open('data/chunks.json', encoding='utf-8') as f:
    chunks = json.load(f)

model = SentenceTransformer('intfloat/multilingual-e5-small')


texts = ['passage: ' + c['text'] + '\n' + c['table_text'] for c in chunks]
embeddings = model.encode(texts, normalize_embeddings=True)
np.save('data/embeddings.npy', embeddings)


def search(question, k=3):
    q = model.encode('query: ' + question, normalize_embeddings=True)
    scores = embeddings @ q
    best = scores.argsort()[::-1][:k]
    for i in best:
        print(round(float(scores[i]), 3), '|', chunks[i]['modul'], '| Seite', chunks[i]['page'])

for i, c in enumerate(chunks):
    text = texts[i]
    result = model.tokenizer(text)
    ids = result['input_ids']
    tokens = len(ids)
    if 'Datenbank' in c['modul'] or tokens > 512:
        print(i, tokens, c['modul'][:60])

question='Wie viel cp hat databases'
search(question)
q='wie viel cp hat algorithmen und datenstrukturen'
search(q)
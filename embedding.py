from sentence_transformers import SentenceTransformer
import numpy as np
import json
import os

with open('data/chunks.json', encoding='utf-8') as f:
    chunks = json.load(f)

model = SentenceTransformer('intfloat/multilingual-e5-small')
# model = SentenceTransformer('BAAI/bge-m3') viel zu langsam

texts = ['passage: ' + c['modul'] +' ' + c['text'] + ' ' + c['table_text'] for c in chunks]

if os.path.exists('data/embeddings.npy'):
    embeddings = np.load('data/embeddings.npy')
else:
    embeddings = model.encode(texts, normalize_embeddings=True)
    np.save('data/embeddings.npy', embeddings)

# embeddings = model.encode(texts, normalize_embeddings=True)
# np.save('data/embeddings.npy', embeddings)

#score vergleicht die ähnlichkeit der frage zu chunk
def search(question, k=3):
    q = model.encode('query: ' + question, normalize_embeddings=True)
    scores = embeddings @ q
    found = []
    for b in scores.argsort()[::-1]:
        if chunks[b]['modul'] not in found:
            found.append(chunks[b]['modul'])
        if len(found) == k:
            break
    return found

for i, c in enumerate(chunks):
    text = texts[i]
    result = model.tokenizer(text)
    ids = result['input_ids']
    tokens = len(ids)
    if tokens > 512:
        print(i, tokens, c['modul'][:60])


with open('data/eval_questions.json', encoding='utf-8') as f:
    eval_data = json.load(f)

tests = eval_data['tests']
final_tests = eval_data['final_tests']


hits = 0
for question, expected in tests:
    found=search(question)
    for f in found:
        if f in expected:
            hits += 1
            break
    else:
        print(f'{question}: {found} ')
print(f'Hitrate wenn wenn die in den ersten 3 chunks gesucht werden:{hits/len(tests)}')

hits=0
for question, expected in final_tests:
    found=search(question)
    for f in found:
        if f in expected:
            hits += 1
            break
    else:
        print(f'{question}: {found} ')
print(f' finale Hitrate wenn wenn die in den ersten 3 chunks gesucht werden:{hits/len(final_tests)}')

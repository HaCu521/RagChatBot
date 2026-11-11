from sentence_transformers import SentenceTransformer
import numpy as np
import json
import os

with open('data/chunks.json', encoding='utf-8') as f:
    chunks = json.load(f)

model = SentenceTransformer('intfloat/multilingual-e5-small')

texts = ['passage: ' + c['modul'] +  c['text'] + '\n' + c['table_text'] for c in chunks]

if os.path.exists('data/embeddings.npy'):
    embeddings = np.load('data/embeddings.npy')
else:
    embeddings = model.encode(texts, normalize_embeddings=True)
    np.save('data/embeddings.npy', embeddings)

#score vergleicht die ähnlichkeit der frage zu chunk
def search(question, k=3,show_answers=False):
    q = model.encode('query: ' + question, normalize_embeddings=True)
    scores = embeddings @ q
    best = scores.argsort()[::-1][:k]
    if show_answers:
        for b in best:
            print(round(float(scores[b]), 3), '|', chunks[b]['modul'], '| Seite', chunks[b]['page'])
    return [chunks[b]['modul'] for b in best]

for i, c in enumerate(chunks):
    text = texts[i]
    result = model.tokenizer(text)
    ids = result['input_ids']
    tokens = len(ids)
    if tokens > 512:
        print(i, tokens, c['modul'][:60])

#wie akkurat die embeddings sind
tests = [
    ('Wie viele CP hat Datenbanken?', ['Modul 14 Databases', 'Modulhandbuch Übersicht']),
    ('Wie lange dauert die Klausur in Algebra?', ['Modul 1 Algebra', 'Modulhandbuch Übersicht']),
    ('Wer ist für IT-Sicherheit zuständig?', ['Module 19 IT Security']),
    ('In welchem Semester belege ich Statistik?', ['Modul 12 Statistics', 'Modulhandbuch Übersicht']),
    ('Welche Voraussetzungen brauche ich für das Informatik-Projekt?', ['Modul 25 Informatik Projekt']),
    ('Lerne ich SQL im Studium?', ['Modul 14 Databases']),
    ('Wo lerne ich etwas über Turingmaschinen?', ['Modul 10 Theoretische Informatik, Automaten und formale Sprachen']),
    ('Wie lange dauert die Praxisphase?', ['Modul 28 Praxisphase']),
    ('In welchem Modul geht es um die DSGVO und Datenschutz?', ['Modul 23 Recht und Datenschutz']),
    ('Muss ich für Operating Systems vorher etwas bestanden haben?', ['Module 16 Operating Systems']),
]


hits = 0
for question, expected in tests:
    found=search(question)
    for f in found:
        if f in expected:
            hits += 1
            break
    else:
        print(f'{question}: {found} ')
print(f'Hitrate:{hits/len(tests)}')



# question='Wie viel cp hat databases'
# search(question)
# q='wie viel cp hat algorithmen und datenstrukturen'
# search(q)
import json
from embedding import search_db, chunks, texts, model


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
    found = [c['modul'] for c in search_db(question)]
    for f in found:
        if f in expected:
            hits += 1
            break
    else:
        print(f'{question}: {found} ')
print(f'Hitrate wenn wenn die in den ersten 3 chunks gesucht werden:{hits/len(tests)}')

hits = 0
for question, expected in final_tests:
    found = [c['modul'] for c in search_db(question)]
    for f in found:
        if f in expected:
            hits += 1
            break
    else:
        print(f'{question}: {found} ')
print(f' finale Hitrate wenn wenn die in den ersten 3 chunks gesucht werden:{hits/len(final_tests)}')
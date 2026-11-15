import ollama
from embedding import search_db, chunks

def ask_llm(question):
    found = search_db(question, k=3, dedup=False)
    top = found[0]['modul']
    if top != 'Modulhandbuch Übersicht':
        #bestes modul komplett für mehr kontext
        found = [c for c in chunks if c['modul'] == top] + [c for c in found if c['modul'] != top]

    context = ''
    for c in found:
        print('Gefunden:', c['modul'], c['page'])
        context += f"[Quelle: {c['modul']}, Seite {c['page']}, {c['fassung']}]\n{c['text']}\n{c['table_text']}\n\n"

    system = f"""You answer questions about a university module handbook.
Use ONLY the excerpts below. Keep the answer short and name the source (module, page, version) at the end.
If someone asks about the workload of a module, give the total workload of the whole module, not of a single unit.
If the answer is not in the excerpts, say so and refer to the examination office (Prüfungsamt).
Always reply in the language of the user's question.

Excerpts:
{context}"""

    response = ollama.chat(model='gemma3:4b',
                           messages=[{'role': 'system', 'content': system},
                                     {'role': 'user', 'content': question}],
                           options={'num_ctx': 8192, 'temperature': 0,'stream': True})
    return response['message']['content']

# while True:
#     question = input('\nFrage: ')
#     if question == 'exit':
#         break
#     print(ask_llm(question))

import json

eval_data = json.load(open('data/eval_questions.json', encoding='utf-8'))

for question, expected in eval_data['tests'][:5]:
    print('\nFrage:', question)
    print(ask_llm(question))
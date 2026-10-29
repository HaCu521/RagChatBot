import pdfplumber
import re
import json

path="data/Modulhandbuch_2023.pdf"


def read_pdf(filename):
    pages = []
    with pdfplumber.open(filename) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            table = page.extract_tables()
            pages.append({'page': page.page_number, 'text': text, 'table': table})
    return pages

def clean_text(pages):
    for p in pages:
        p['text']=re.sub(r'Seite \d+/\d+','',p['text'])
        p['text']=re.sub(r'Modulhandbuch zum Studiengang Informatik \(B\.Sc\.\)','',p['text'])
        p['text']=re.sub(r'Stand: \d+\.\d+\.\d+','',p['text'])
        p['text']=re.sub(r'Frankfurt University of Applied Sciences – Fachbereich 2, Informatik und Ingenieurwissenschaften','',p['text'])
        p['text']=re.sub(r'-\n(?=[a-zäöüß])','',p['text'])
        p['text'] = re.sub(r'•\n', '• ', p['text'])
        p['text']=re.sub(r' +\n', '\n', p['text'])
        p['text']=re.sub(r'\n+', '\n', p['text'])
        p['text'] = p['text'].strip()
    return pages

def clean_table(pages):
    for p in pages:
        for t in p['table']:
            for r in t:
                for i, c in enumerate(r):
                    if c:
                        r[i] = re.sub(r'\n(?!•)', ' ', c)
            t[:] = [r for r in t if r[1]]
    return pages


def chunk_modules(pages):
    chunks =[]
    modules={'page':[], 'text':'', 'table':[]}#quellen angabe spaeter im zahlenbereich, weil set keine zahlen mehrfach hat!!

    for p in pages:
        for t in p['text'].split('\n'): #split um Zeile fuer Zeile zu untersuchen
            if re.match(r'Module? \d+',t):
                if modules["text"]:
                    chunks.append(modules)
                    modules={'page':[], 'text':'','table':[]}
            if p['page'] not in modules['page']:
                modules['page'].append(p['page'])
            modules['text']+=t
        modules['table'].append(p['table'])#temporare loesung, tables verrutschen leicht bei seite, aber kp weil focus on text

    if modules["text"]:
        chunks.append(modules)
            
    return chunks

def save_chunks(chunks):
    with open(chunks,'data/','w','encoding="utf-8') as f:
        json.dump(chunks, f,ensure_ascii=False,indent=4)






pages = read_pdf(path)
pages= clean_text(pages)
# print(pages[2]['text'])
# print(pages[20]['table'])


chunks = chunk_modules(pages)
c = chunks[2]

print(c['text'])
print(c['page'])
print(c['table'])



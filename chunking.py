import pdfplumber
import re
import json


path="data/MHB_BA_Informatik_2012_Stand_2022-11-23.pdf"

def read_pdf(filename):
    pages = []
    with pdfplumber.open(filename) as pdf:
        for page in pdf.pages:
            found = page.find_tables()
            table = [t.extract() for t in found]
            lines = []
            for l in page.extract_text_lines():
                in_table = any(t.bbox[1] <= l['top'] <= t.bbox[3] for t in found)
                if not in_table or re.match(r'Module? \d+', l['text']):  #tabellentext raus,ueberschrift bleibt
                    lines.append((l['top'], l['text']))
            for i, t in enumerate(found):
                lines.append((t.bbox[3], f'TABLE_{i}'))  #platzhalter an position der tabelle
            lines.sort()
            text = '\n'.join(l[1] for l in lines)
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
    current_modul = 'Modulhandbuch Übersicht'
    modules = {'page': [], 'text': '', 'table': [], 'modul': current_modul}#quellen angabe spaeter im zahlenbereich, weil set keine zahlen mehrfach hat!!

    for p in pages:
        for t in p['text'].split('\n'): #split um Zeile fuer Zeile zu untersuchen
                is_module= re.match(r'Module? \d+',t)  and not re.search(r'\.{3,}\s*\d+$', t)
                is_unit=re.match(r'Unitbeschreibung|Unit description|Description of the unit', t)
                if is_module:
                    current_modul=t

                if is_unit or is_module:
                    if modules["text"]:
                        chunks.append(modules)
                        modules={'page':[], 'text':'','table':[],'modul':current_modul}
                if p['page'] not in modules['page']:
                    modules['page'].append(p['page'])
                if t.startswith('TABLE_'):
                        modules['table'].append(p['table'][int(t[6:])])
                        continue
                modules['text']+=t+'\n'


    if modules["text"]:
        chunks.append(modules)
            
    return chunks

def table_to_text(tables):
    lines = []
    for t in tables:
        for r in t:
            lines.append(f'{r[0]}: {r[1]}')
    return '\n'.join(lines) #list zu string

def split_chunks(chunks, max_words=250, overlap=20):
    result = []
    for c in chunks:
        words = (c['text'] + '\n' + c['table_text']).split()
        if len(words) <= max_words:
            result.append(c)
            continue
        for start in range(0, len(words), max_words - overlap):
            part = dict(c)
            part['text'] = ' '.join(words[start:start + max_words])
            part['table_text'] = ''
            result.append(part)
    return result

def save_chunks(chunks):
    with open('data/chunks.json','w',encoding='utf-8') as f:
        json.dump(chunks, f,ensure_ascii=False,indent=4)



pages = read_pdf(path)
pages= clean_text(pages)
pages=clean_table(pages)


chunks = chunk_modules(pages)

# Metadaten für Quellenangabe
for c in chunks:
    c['table_text'] = table_to_text(c['table'])
    c['dokument'] = 'Modulhandbuch Informatik (B.Sc.)'
    c['fassung'] = 'PO 2012, Stand 23.11.2022'#

chunks=split_chunks(chunks,210,20)
save_chunks(chunks)
c = chunks[2]
print(len(chunks))
print(c['text'])
print(c['page'])
print(c['table'])
print(c['table_text'])
print(c['modul'], '|', c['fassung'], '|', c['page'])  #Metadaten prüfen


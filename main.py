
import pdfplumber
import re

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
        p['text']=re.sub(r'Mod  ulhandbuch zum Studiengang Informatik \(B\.Sc\.\)','',p['text'])
        p['text']=re.sub(r'Stand: \d+\.\d+\.\d+','',p['text'])
        p['text']=re.sub(r'Frankfurt University of Applied Sciences – Fachbereich 2, Informatik und Ingenieurwissenschaften','',p['text'])
        p['text']=re.sub(r'-\n(?=[a-zäöüß])','',p['text'])
        p['text'] = re.sub(r'•\n', '• ', p['text'])
        p['text']=re.sub(r' +\n', '\n', p['text'])
        p['text']=re.sub(r'\n+', '\n', p['text'])
        p['text'] = p['text'].strip()
    return pages

# def clean_table(pages):


pages = read_pdf(path)
pages= clean_text(pages)
# print(pages[2]['text'])
print(pages[20]['table'])
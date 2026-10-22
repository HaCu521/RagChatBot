import pymupdf
import re

path="data/Modulhandbuch_2023.pdf"


def read_pdf(filename):
    pages=[]
    doc = pymupdf.open(filename)
    for i in range(len(doc)):
        page_number=i+1
        text = doc.get_page_text(i)
        table = []
        page = doc.load_page(i)
        table_finder = page.find_tables()
        if table_finder.tables:
            for t in table_finder.tables:
                table.append(t.extract())
        pages.append({'page':page_number,'text':text,'table':table})
    doc.close()
    return pages


pages = read_pdf(path)
print(pages[2]["page"])
import pymupdf

pdf="Modulhandbuch.pdf"


def readpdf(filename):
    doc = pymupdf.open(filename)
    for i in range(len(doc)):
        text=doc.get_page_text(i)
        page=doc.load_page(i)
        table=page.find_tables(strategy='lines')
        if table is not (type (None)):
            tt = table.textpage.extractText()

        #tp = tt.ex
        #print(i,text[:400])
        print(tt)

readpdf(pdf)
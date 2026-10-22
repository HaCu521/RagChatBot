import pymupdf

pdf="Modulhandbuch.pdf"


def readpdf(filename):
    tt=[]
    doc = pymupdf.open(filename)
    for i in range(len(doc)):
        #text=doc.get_page_text(i)
        page=doc.load_page(i)
        table_finder=page.find_tables(strategy='lines')
        if table_finder.tables :
            for t in table_finder.tables:
                tt.append(t.extract())

        #print(i)
        #print(i,text[:400])
    print(tt)

readpdf(pdf)
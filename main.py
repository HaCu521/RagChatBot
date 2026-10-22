import pymupdf

pdf=("data/Modulhandbuch_2023.pdf")


def readpdf(filename):
    tt=[]
    doc = pymupdf.open(filename)
    for i in range(len(doc)):
        text=doc.get_page_text(i)
        page=doc.load_page(i)
        table_finder=page.find_tables(strategy='lines')
        if table_finder.tables :
            for t in table_finder.tables:
                tt.append(t.extract())
                print(tt)

        print(i)
        print(i,text[:400])
        print(tt)
    doc.close()

readpdf(pdf)
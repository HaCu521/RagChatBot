from sentence_transformers import SentenceTransformer

model = SentenceTransformer('intfloat/multilingual-e5-small')
vector = model.encode('Datenbanken hat 5 Credit Points')
print(len(vector))
print(vector[:5])
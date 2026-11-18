# RAG-Chatbot für das Modulhandbuch (FRA-UAS Informatik B.Sc.)

Ein Chatbot, der Fragen zum Modulhandbuch des Informatik-Studiengangs der Frankfurt University of Applied Sciences beantwortet – auf Deutsch und Englisch, mit Quellenangabe (Modul, Seite, Fassung). Der Bot antwortet **ausschließlich** aus den Dokumenten und sagt ehrlich, wenn er etwas nicht findet.

Beispiel: *„Wie viele CP hat Databases?“* → *„5 CP. (Modul 14 Databases, Seite 58, PO 2012, Stand 23.11.2022)“*

---

## Funktionen

- Fragen in Alltagssprache, Antwort mit Quelle
- Zweisprachig: Antwort in der Sprache der Frage (Deutsch/Englisch)
- Keine Halluzinationen: antwortet nur aus dem Modulhandbuch, sonst Verweis ans Prüfungsamt
- Läuft vollständig lokal (keine Daten verlassen den Rechner)

---

## Architektur

```
Browser
   │  Frage
   ▼
Streamlit (Frontend)
   │  POST /ask  (JSON, REST)
   ▼
FastAPI (Backend)
   │
   ├─▶ Retrieval:  Frage → Embedding (bge-m3) → Ähnlichkeitssuche in pgvector
   │
   └─▶ Generation: gefundene Chunks + Frage → LLM (Ollama / gemma3) → Antwort
   │
   ▼
Antwort mit Quelle (JSON) → zurück ans Frontend
```

Frontend und Backend sind bewusst getrennt: Das Backend ist eine REST-API, das Frontend ruft sie auf. So lässt sich das Frontend austauschen, ohne das Backend zu ändern.

---

## Pipeline (wie die Daten vorbereitet werden)

1. **PDF einlesen** (`pdfplumber`): Text und Tabellen extrahieren, Tabellen über ihre Position auf der Seite dem richtigen Modul zuordnen.
2. **Chunking**: strukturbasiert – ein Chunk pro Unit (Vorlesung, Übung), erkannt an den Unit-Überschriften; zu lange Chunks zusätzlich mit Überlappung geteilt. Tabellen werden mit Spaltennamen in Text umgewandelt.
3. **Embeddings** (`sentence-transformers`, bge-m3): jeder Chunk wird zu einem Vektor.
4. **Speichern** in PostgreSQL mit der pgvector-Erweiterung (in Docker).
5. **Suche**: Frage einbetten, per Cosinus-Ähnlichkeit (`<=>`) die passenden Chunks aus der Datenbank holen.
6. **Antwort**: Chunks + Frage als Prompt an ein lokales LLM (Ollama, gemma3), das daraus eine Antwort mit Quelle formuliert.

---

## Evaluation

Gemessen mit **Hit Rate@3** (Anteil der Testfragen, bei denen die richtige Quelle unter den Top 3 ist). Testfragen in `data/eval_questions.json`, ein Drittel als Holdout zurückgehalten.

| Variante | Hit Rate@3 | Anmerkung |
|---|---|---|
| multilingual-e5-small | 0,90 | Ausgangswert (20 Fragen) |
| + Deduplizierung (jedes Modul nur einmal) | 0,95 | |
| + 5 englische Fragen | 0,92 | 25 Fragen, cross-linguale Fälle schwieriger |
| **bge-m3 (Embedding-Wechsel)** | **0,96** | cross-linguale Fragen gelöst |
| Holdout (10 unbekannte Fragen) | 1,00 | |

Entscheidung: **bge-m3**, weil es deutsche Fragen zu englisch benannten Modulen (z. B. „IT-Sicherheit“ → „IT Security“) zuverlässig findet, bei denen e5-small scheiterte.

---

## Tech-Stack

- **Python**
- **sentence-transformers** (bge-m3) – Embeddings / semantische Suche
- **PostgreSQL + pgvector** – Vektordatenbank
- **Docker** – Datenbank-Container
- **Ollama** (gemma3) – lokales LLM
- **FastAPI** + **Pydantic** – REST-API-Backend
- **Streamlit** – Frontend
- **Git**

---

## Starten

Voraussetzungen: Python mit virtueller Umgebung, Docker, Ollama.

```bash
# 1. Datenbank-Container starten (einmalig angelegt, danach nur noch starten)
docker start mhb-db

# 2. Daten in die Datenbank laden (nur beim ersten Mal oder nach Änderungen am Chunking)
python chunking.py        # erzeugt data/chunks.json
python db_load.py         # lädt Chunks + Vektoren in die DB

# 3. LLM-Modell bereitstellen (einmalig)
ollama pull gemma3:4b

# 4. Backend starten
uvicorn main:app --reload

# 5. Frontend starten (zweites Terminal)
streamlit run frontend.py
```

Frontend: `http://localhost:8501` · Backend-Doku: `http://localhost:8000/docs`

---

## Bekannte Grenzen

- Das lokale LLM (gemma3 auf CPU) braucht pro Antwort einige Sekunden. Für schnellere Antworten ließe sich ein kleineres Modell oder eine LLM-API anbinden.
- Einzelne cross-linguale Fragen zu gleichnamigen Modulen können danebenliegen (Retrieval-Grenze des Embedding-Modells).
- Antworten aus der Übersichtstabelle haben eine ungenauere Seitenangabe als modulspezifische Chunks.

## Mögliche Erweiterungen

- Prüfungsordnung als zweites Dokument aufnehmen
- Zugangsdaten in eine `.env` auslagern
- Hybrid Search (Embeddings + BM25) für exakte Begriffe

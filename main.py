from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from chatbot import ask_llm

app = FastAPI()

class Question(BaseModel):
    question: str
@app.get("/")
def read_root():
    return {"status": "RagChatBot is running"}
@app.get("/health")
def health():
    return {"status": "ok"}
@app.post("/ask")
def ask(q: Question):
    if not q.question.strip():
        raise HTTPException(status_code=400, detail="question is required.")
    try:
        return {"answer": ask_llm(q.question)}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"problem: {e}")
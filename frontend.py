import streamlit as st
import requests

st.title("Fra-Uas Chatbot zu Modulhandbuch")

question=st.text_input("Was möchtest du wissen?")

if question:
    with st.spinner("Ich suche im Modulhandbuch..."):
        answer = requests.post("http://127.0.0.1:8000/ask", json={"question": question}).json()
    st.write(answer["answer"])





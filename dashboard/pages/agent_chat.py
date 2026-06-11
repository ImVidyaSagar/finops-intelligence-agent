import streamlit as st
from agent.graph import answer_question

st.title("🤖 FinOps AI Agent")

query = st.text_input("Ask a question")

if query:
    response = answer_question(query)
    st.markdown(f"**🤖 Answer:**\n\n{response}")
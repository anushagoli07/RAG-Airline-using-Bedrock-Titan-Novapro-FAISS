import streamlit as st
from main import get_response, initialize_vectorstore

st.set_page_config(page_title="Airline RAG Chatbot", layout="wide")

st.title("Airline RAG Chatbot")
st.markdown("Ask any question about airlines based on the provided documents.")

# Initialize vectorstore on first run
if 'vectorstore' not in st.session_state:
    with st.spinner("Initializing vectorstore..."):
        st.session_state.vectorstore = initialize_vectorstore()

question = st.text_input("Enter your question here:")

if st.button("Ask"):
    if question.strip() == "":
        st.warning("Please enter a question before asking.")
    else:
        with st.spinner("Getting response..."):
            try:
                result = get_response(question, st.session_state.vectorstore)
                st.markdown("### Response:")
                st.write(result['output']['message']['content'][0]['text'])
            except Exception as e:
                st.error(f"An error occurred: {e}")
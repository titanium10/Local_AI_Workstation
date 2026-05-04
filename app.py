import streamlit as st
import time
import requests # Used to talk to Ollama
from duckduckgo_search import DDGS

# 1. Page Configuration
st.set_page_config(page_title="Samrat's AI Assistant", page_icon="🤖")
st.title("Samrat's AI Assistant 🤖")

# 2. Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# 3. Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 4. Chat Input
if prompt := st.chat_input("Ask me anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 5. The "Brain" Logic (Search + Llama 3)
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        with st.spinner("Thinking..."):
            # Step A: Get Web Context
            search_context = ""
            try:
                with DDGS() as ddgs:
                    results = list(ddgs.text(prompt, max_results=3))
                    search_context = "\n".join([r['body'] for r in results])
            except:
                search_context = "No internet results found."

            # Step B: Talk to Local Llama 3 via Ollama
            try:
                # This is the "System Prompt" that tells the AI how to behave
                full_prompt = f"""
                You are a helpful AI assistant. 
                Use the following web search results to answer the user's question accurately.
                If the search results don't help, use your own knowledge.
                
                Search Results: {search_context}
                
                User Question: {prompt}
                """
                
                response = requests.post(
                    "http://localhost:11434/api/generate",
                    json={
                        "model": "llama3", # Or "phi3"
                        "prompt": full_prompt,
                        "stream": False
                    }
                )
                ai_answer = response.json()['response']
            except Exception as e:
                ai_answer = f"I couldn't connect to Llama 3. Make sure Ollama is running! Error: {e}"

        # 6. Typewriter Effect
        full_response = ""
        for word in ai_answer.split(' '):
            full_response += word + " "
            time.sleep(0.01)
            message_placeholder.markdown(full_response + "▌")
        
        message_placeholder.markdown(full_response)
    
    st.session_state.messages.append({"role": "assistant", "content": ai_answer})
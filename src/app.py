import streamlit as st
from query import query_rag_pipeline

# 1. Setup the Web Page
st.set_page_config(page_title="Document Q&A Bot", page_icon="🤖")
st.title("🤖 Document Q&A Bot")
st.markdown("Ask questions about your uploaded documents! (e.g., your resume)")

# 2. Initialize Chat History
# Streamlit re-runs the whole script every time you click something, 
# so we use 'session_state' to remember the chat history.
if "messages" not in st.session_state:
    st.session_state.messages = []

# 3. Display Previous Messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 4. Handle User Input
if prompt := st.chat_input("What are this candidate's skills?"):
    
    # Show the user's question on screen and save it to history
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Show the AI's response container
    with st.chat_message("assistant"):
        # Add a cool loading spinner!
        with st.spinner("Searching documents..."):
            try:
                # Call the exact same pipeline we built earlier
                result = query_rag_pipeline(prompt)
                
                answer = result["answer"]
                unique_citations = set(result["citations"])
                
                # Format the text so it looks nice on the web
                full_response = f"{answer}\n\n**Sources Used:**\n"
                for citation in unique_citations:
                    full_response += f"- *{citation}*\n"
                
                # Print to screen and save to history
                st.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                
            except Exception as e:
                error_msg = f"An error occurred: {e}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
import streamlit as st
from query import query_rag_pipeline

# 1. PAGE CONFIG (Must be the very first Streamlit command)
st.set_page_config(
    page_title="Knowledge Explorer",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="expanded"
)

# 2. PREMIUM CSS UPGRADE
st.markdown("""
<style>
    /* 1. Gorgeous subtle background gradient for the main app */
    .stApp {
        background: linear-gradient(135deg, #fdfbfb 0%, #ebedee 100%);
    }
    
    /* 2. Transparent top header so the gradient shows through */
    header {
        background-color: transparent !important;
    }
    
    /* 3. Style the main title with a beautiful painted text gradient */
    .main-title {
        font-family: 'Georgia', serif;
        font-size: 3.2rem;
        background: -webkit-linear-gradient(45deg, #D4145A, #FBB03B);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        font-weight: 800;
        margin-bottom: -10px;
        padding-top: 10px;
    }
    
    /* 4. Elegant subtitle with letter spacing */
    .sub-title {
        font-size: 1.1rem;
        color: #5D6D7E;
        text-align: center;
        letter-spacing: 1.5px;
        margin-top: 10px;
        margin-bottom: 40px;
        font-style: italic;
    }
    
    /* 5. Style the sidebar with a soft warm color and subtle border */
    [data-testid="stSidebar"] {
        background-color: #FFF9F5;
        border-right: 1px solid #FFE4D6;
    }
    
    /* 6. Style the chat input box to look more like a custom pill/bubble */
    [data-testid="stChatInput"] {
        border: 2px solid #FFD1BA !important;
        border-radius: 25px !important;
        background-color: #FFFFFF !important;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.05);
    }
    
    /* Hide default Streamlit footers */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# 3. CHARMING SIDEBAR
with st.sidebar:
    st.title("🌸 Welcome!")
    st.markdown("Hello! I am a custom-built AI research assistant.")
    st.markdown("---")
    st.markdown("### 📚 What I Know:")
    st.markdown("I have been trained on a specific set of private documents, including:")
    st.markdown("- Resume details\n- SSC CGL Solved Papers\n- Exam Admit Cards\n- Mandala Art guides")
    st.markdown("---")
    st.markdown("### 💡 Try asking:")
    st.info('"What are the hobbies of this candidate?"')
    st.info('"Where is the TCS IPA exam located?"')
    st.markdown("---")
    st.caption("Built with ❤️ using Streamlit, ChromaDB, and Gemini.")

# 4. MAIN HEADER
st.markdown('<p class="main-title">✨ Document Explorer</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Ask me anything about the uploaded knowledge base!</p>', unsafe_allow_html=True)

# 5. INITIALIZE CHAT HISTORY
if "messages" not in st.session_state:
    st.session_state.messages = []

# 6. DISPLAY PREVIOUS MESSAGES WITH CUSTOM AVATARS
for message in st.session_state.messages:
    # Use a cute avatar depending on who is talking
    avatar = "🎒" if message["role"] == "user" else "🪄"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# 7. HANDLE USER INPUT & CALL DATABASE
if prompt := st.chat_input("Ask a question about the documents..."):
    
    # Show the user's question on screen and save it to history
    with st.chat_message("user", avatar="🎒"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Show the AI's response container
    with st.chat_message("assistant", avatar="🪄"):
        # Add a charming loading spinner!
        with st.spinner("Flipping through the pages... 📖"):
            try:
                # Call your exact working pipeline
                result = query_rag_pipeline(prompt)
                
                answer = result["answer"]
                unique_citations = set(result["citations"])
                
                # Format the text with citations
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
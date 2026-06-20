import streamlit as st
import os
from query import query_rag_pipeline

st.set_page_config(
    page_title="Knowledge Explorer",
    page_icon="🫧",
    layout="centered",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* 1. Aurora Glowing Background */
    .stApp {
        background-color: #f6f8fb;
        background-image: 
            radial-gradient(at 40% 20%, hsla(280,100%,74%,0.15) 0px, transparent 50%),
            radial-gradient(at 80% 0%, hsla(189,100%,56%,0.15) 0px, transparent 50%),
            radial-gradient(at 0% 50%, hsla(355,100%,93%,0.15) 0px, transparent 50%);
        background-attachment: fixed;
    }
    
    /* 2. Transparent Header */
    header {
        background-color: transparent !important;
    }
    
    /* 3. Frosted Glass Sidebar */
    [data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.4) !important;
        backdrop-filter: blur(20px) !important;
        -webkit-backdrop-filter: blur(20px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.5) !important;
    }
    
    /* 4. Elegant Main Title */
    .main-title {
        font-family: 'Helvetica Neue', sans-serif;
        font-size: 3.5rem;
        background: -webkit-linear-gradient(120deg, #a18cd1 0%, #fbc2eb 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        font-weight: 800;
        letter-spacing: -1.5px;
        margin-bottom: 0px;
        padding-top: 10px;
    }
    
    /* 5. Minimalist Subtitle */
    .sub-title {
        font-family: 'Helvetica Neue', sans-serif;
        font-size: 1.1rem;
        color: #7f8c8d;
        text-align: center;
        font-weight: 300;
        letter-spacing: 1px;
        margin-top: 5px;
        margin-bottom: 40px;
    }
    
    /* 6. Frosted Glass Chat Messages */
    [data-testid="stChatMessage"] {
        background: rgba(255, 255, 255, 0.6) !important;
        backdrop-filter: blur(10px) !important;
        -webkit-backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(255, 255, 255, 0.8) !important;
        border-radius: 20px !important;
        padding: 15px !important;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.05) !important;
        margin-bottom: 15px;
    }
    
    /* 7. Floating Chat Input Pill */
    [data-testid="stChatInput"] {
        border: 1px solid rgba(255, 255, 255, 0.8) !important;
        background: rgba(255, 255, 255, 0.8) !important;
        backdrop-filter: blur(15px) !important;
        border-radius: 30px !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08) !important;
        padding: 5px !important;
    }
    
    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.title("☁️ Explorer")
    st.markdown("Your private, AI-powered knowledge base.")
    st.markdown("---")
    st.markdown("### 📚 Indexed Files:")
    
    # Dynamically read files from the data folder!
    
    try:
        data_files = os.listdir("data")
        valid_files = [f for f in data_files if f.endswith('.pdf') or f.endswith('.docx')]
        if valid_files:
            for file in valid_files:
                st.markdown(f"• {file}")
        else:
            st.markdown("• No documents found.")
    except Exception:
        st.markdown("• No documents found.")

    st.markdown("---")
    st.markdown("### 💡 Example Queries:")
    st.info('"What are the hobbies of this candidate?"')
    st.info('"Where is the TCS IPA exam located?"')
    st.markdown("---")
    st.caption("Powered by Streamlit & Gemini 🫧")

st.markdown('<p class="main-title">Nexus</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Intelligent Document Retrieval</p>', unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    avatar = "👤" if message["role"] == "user" else "✨"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

if prompt := st.chat_input("Type your question here..."):
    
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant", avatar="✨"):
        with st.spinner("Synthesizing knowledge... 🫧"):
            try:
                result = query_rag_pipeline(prompt)
                
                answer = result["answer"]
                unique_citations = set(result["citations"])
                
                full_response = f"{answer}\n\n**Sources:**\n"
                for citation in unique_citations:
                    full_response += f"- *{citation}*\n"
                
                st.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                
            except Exception as e:
                error_msg = f"An error occurred: {e}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
# 🤖 Document Q&A Bot (RAG Pipeline)

## 📌 Project Overview

This project is a full-stack Retrieval-Augmented Generation (RAG) system. It allows users to upload PDF documents (like resumes or reports...) and ask natural language questions about them. The bot retrieves the most relevant context from the documents and uses an LLM to generate a grounded, accurate answer with inline citations.

## ⚙️ Tech Stack

- **Language:** Python 3.11+
- **Document Processing:** `pypdf`
- **Vector Database:** `chromadb` (Persistent Local Storage)
- **Embeddings:** Google `gemini-embedding-001`
- **LLM:** Google `gemini-2.5-flash`
- **Frontend UI:** `streamlit`

## 🚀 Setup & Installation

**1. Clone the repository**

git clone <your-github-repo-link-here>
cd document-qa-bot

**2. Create and activate a virtual environment**

# Windows

python -m venv venv
venv\Scripts\activate

# macOS/Linux

python -m venv venv
source venv/bin/activate

**3. Install dependencies**

pip install -r requirements.txt

**4. Set up environment variables**

Create a .env file in the root directory and add your Google Gemini API key:
GEMINI_API_KEY="ACTUAL_KEY"

## 🧠 How to Run the Project

Step 1: Ingest Documents
Place your PDF files inside the data/ folder, then run the ingestion script to chunk the text and build the local vector database:
python src/ingest.py

Step 2: Start the Q&A Interface
You can interact with the bot in two ways:

Terminal UI: Run python src/main.py for a command-line chat loop.

Web UI (Streamlit): Run streamlit run src/app.py for a fully interactive web interface.

## 📊 Analysis & Architecture

The RAG Pipeline
Extraction: The pypdf library reads raw PDFs page-by-page, stripping whitespace while preserving crucial metadata (filename and page number).

Chunking: Text is split using recursive character chunking (1000 characters with a 200-character overlap) to ensure semantic boundaries are maintained without losing context.

Embedding & Storage: Chunks are vectorized using Google's gemini-embedding-001 model and stored locally using ChromaDB, eliminating the need to re-embed documents on every query.

Retrieval & Generation: When a user asks a question, it is embedded and matched against the vector database using cosine similarity. The top 3 chunks are injected into a strict system prompt, forcing the gemini-2.5-flash model to answer only using the provided context and to cite its sources.

### Challenges Overcome

1. **API Deprecation & Compatibility:** During development, I encountered API deprecation issues with older Google generative AI models (`text-embedding-004` and `gemini-1.5-flash`). To solve this, I bypassed ChromaDB's default wrapper and built a custom embedding function class to interface directly with the newest, live Google GenAI endpoints (`gemini-embedding-001` and `gemini-2.5-flash`), ensuring the pipeline remained up-to-date.

2. **API Rate Limiting:** When scaling up the ingestion pipeline to handle multiple PDF documents simultaneously, I hit a `429 ResourceExhausted` error due to Google Gemini's free-tier quota limits (100 requests/minute). To solve this, I engineered a rate-limiting fallback in the `save_to_vector_db` function. By grouping the text chunks into smaller batches and introducing a deliberate `time.sleep()` delay between uploads, the script now safely processes large document libraries without crashing or dropping data.

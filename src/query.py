import os
import chromadb
from chromadb.api.types import Documents, EmbeddingFunction, Embeddings
import google.generativeai as genai
from dotenv import load_dotenv

# Load API Key
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

# We must use the exact same custom function so the math matches the database!
class CustomGeminiEmbeddingFunction(EmbeddingFunction):
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        
    def __call__(self, input: Documents) -> Embeddings:
        result = genai.embed_content(
            model="models/gemini-embedding-001",
            content=input,
            task_type="retrieval_query" 
        )
        return result['embedding']

def query_rag_pipeline(user_query: str, db_path: str = "db", k: int = 3) -> dict:
    """
    Searches the database, builds a grounded prompt, and queries the LLM.
    """
    # 1. Connect to the database
    client = chromadb.PersistentClient(path=db_path)
    embedding_fn = CustomGeminiEmbeddingFunction(api_key=api_key)

    collection = client.get_collection(
        name="document_knowledge_base",
        embedding_function=embedding_fn
    )

    # 2. Search for the top 3 closest text chunks
    results = collection.query(
        query_texts=[user_query],
        n_results=k
    )

    # 3. Format the retrieved text
    context_blocks = []
    citations = []

    for doc, meta in zip(results['documents'][0], results['metadatas'][0]):
        source_name = meta['source']
        page_num = meta['page']
        citation_str = f"Source: {source_name}, Page: {page_num}"

        context_blocks.append(f"[{citation_str}]\nContext: {doc}")
        citations.append(citation_str)

    context_payload = "\n\n---\n\n".join(context_blocks)

    # 4. Give Gemini strict instructions so it doesn't hallucinate
    system_prompt = (
        "You are a professional, accurate document Q&A assistant. "
        "Answer the user's question using ONLY the provided document context below. "
        "Cite the sources (filenames and pages) inline next to facts you cite. "
        "If the answer cannot be found in the context, clearly state: "
        "'I am sorry, but the provided documents do not contain the answer to your question.' "
        "Do not make up facts or use external knowledge sources."
    )

    prompt = (
        f"{system_prompt}\n\n"
        f"CONTEXT INFORMATION:\n{context_payload}\n\n"
        f"USER QUESTION: {user_query}\n\n"
        f"GROUNDED ANSWER:"
    )

    # 5. Get the answer!
    model = genai.GenerativeModel('gemini-2.5-flash')
    response = model.generate_content(prompt)

    return {
        "answer": response.text,
        "citations": citations
    }

# --- TEST BLOCK ---
if __name__ == "__main__":
    # Change this question to ask anything about your resume!
    question = "What are the core technical skills of this candidate?"
    
    print(f"Searching for: '{question}'...\n")
    
    result = query_rag_pipeline(question)
    
    print("--- AI ANSWER ---")
    print(result["answer"])
    print("\n--- SOURCES USED ---")
    for citation in result["citations"]:
        print(f"- {citation}")
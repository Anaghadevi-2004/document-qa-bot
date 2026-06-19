import os
import glob
import time
import chromadb
from chromadb.api.types import Documents, EmbeddingFunction, Embeddings
import google.generativeai as genai
from dotenv import load_dotenv
from pypdf import PdfReader # <-- This was the missing piece!

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

class CustomGeminiEmbeddingFunction(EmbeddingFunction):
    def __init__(self, api_key: str):
        # Configure the Google AI library directly
        genai.configure(api_key=api_key)
        
    def __call__(self, input: Documents) -> Embeddings:
        # Send the text chunks to Gemini to get the vector embeddings
        result = genai.embed_content(
            model="models/gemini-embedding-001",
            content=input,
            task_type="retrieval_document"
        )
        return result['embedding']

def extract_pdf_pages(file_path: str) -> list[dict]:
    """
    Extracts text page-by-page from a PDF, tracking page numbers and file source.
    """
    extracted_data = []
    file_name = os.path.basename(file_path)

    try:
        reader = PdfReader(file_path)
        for index, page in enumerate(reader.pages):
            text = page.extract_text()
            if text and text.strip():
                clean_text = " ".join(text.split())
                extracted_data.append({
                    "text": clean_text,
                    "metadata": {
                        "source": file_name,
                        "page": index + 1  
                    }
                })
    except Exception as e:
        print(f"Error reading PDF {file_name}: {e}")

    return extracted_data

def chunk_extracted_pages(pages: list[dict], chunk_size: int = 1000, chunk_overlap: int = 200) -> list[dict]:
    """
    Splits page-level documents into smaller, overlapping chunks.
    Ensures that source metadata is carried over to every individual chunk.
    """
    chunks = []

    for page in pages:
        text = page["text"]
        metadata = page["metadata"]

        start = 0
        text_length = len(text)

        while start < text_length:
            # Determine end point
            end = min(start + chunk_size, text_length)
            chunk_text = text[start:end]

            chunks.append({
                "text": chunk_text,
                "metadata": {
                    "source": metadata["source"],
                    "page": metadata["page"],
                    "chunk_range": f"{start}-{end}"
                }
            })

            start += (chunk_size - chunk_overlap)

    return chunks

def save_to_vector_db(chunks: list[dict], db_path: str = "db"):
    """
    Embeds text chunks and saves them into a persistent disk-based ChromaDB in batches to respect API limits.
    """
    client = chromadb.PersistentClient(path=db_path)
    embedding_fn = CustomGeminiEmbeddingFunction(api_key=api_key)

    collection = client.get_or_create_collection(
        name="document_knowledge_base",
        embedding_function=embedding_fn,
        metadata={"hnsw:space": "cosine"} 
    )

    batch_size = 15 
    
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i : i + batch_size]
        
        ids = [f"id_{j}" for j in range(i, i + len(batch))]
        documents = [chunk["text"] for chunk in batch]
        metadatas = [chunk["metadata"] for chunk in batch]

        collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )
        
        # Calculate total batches just so you can see the progress
        total_batches = (len(chunks) + batch_size - 1) // batch_size
        print(f"Indexed batch {i // batch_size + 1} of {total_batches}...")
        
        time.sleep(10) 

    print(f"\nSuccessfully indexed {len(chunks)} chunks in the vector database.")

if __name__ == "__main__":
    # We changed this path to look inside the current project folder!
    data_folder = "data/" 
    all_chunks = []
    
    # 1. Find all PDF files in the data folder
    pdf_files = glob.glob(os.path.join(data_folder, "*.pdf"))
    
    if not pdf_files:
        print("No PDF files found in the data directory!")
    else:
        # 2. Loop through every single PDF and extract/chunk it
        for file_path in pdf_files:
            print(f"Processing: {os.path.basename(file_path)}...")
            extracted_pages = extract_pdf_pages(file_path)
            chunks = chunk_extracted_pages(extracted_pages)
            all_chunks.extend(chunks) 
            
        # 3. Save ALL chunks from ALL documents into the database at once
        print(f"\nSaving a total of {len(all_chunks)} chunks to the database...")
        save_to_vector_db(all_chunks)
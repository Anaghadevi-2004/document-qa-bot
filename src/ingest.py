import os
import glob
import time
import docx
import chromadb
from chromadb.api.types import Documents, EmbeddingFunction, Embeddings
import google.generativeai as genai
from dotenv import load_dotenv
from pypdf import PdfReader 

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

class CustomGeminiEmbeddingFunction(EmbeddingFunction):
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        
    def __call__(self, input: Documents) -> Embeddings:
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
def extract_docx_pages(file_path: str) -> list[dict]:
    """Extracts text from a DOCX file."""
    extracted_data = []
    file_name = os.path.basename(file_path)
    
    try:
        doc = docx.Document(file_path)
        full_text = " ".join([para.text for para in doc.paragraphs if para.text.strip()])
        
        if full_text:
            extracted_data.append({
                "text": full_text,
                "metadata": {
                    "source": file_name,
                    "page": 1 
                }
            })
    except Exception as e:
        print(f"Error reading DOCX {file_name}: {e}")

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
        
        total_batches = (len(chunks) + batch_size - 1) // batch_size
        print(f"Indexed batch {i // batch_size + 1} of {total_batches}...")
        
        time.sleep(10) 

    print(f"\nSuccessfully indexed {len(chunks)} chunks in the vector database.")

if __name__ == "__main__":
    data_folder = "data/" 
    all_chunks = []
    
    # Check if the folder exists
    if not os.path.exists(data_folder):
        print(f"Directory {data_folder} not found!")
    else:
        # Loop through every file in the folder
        for filename in os.listdir(data_folder):
            file_path = os.path.join(data_folder, filename)
            
            if filename.endswith(".pdf"):
                print(f"Processing PDF: {filename}...")
                extracted_pages = extract_pdf_pages(file_path)
                chunks = chunk_extracted_pages(extracted_pages)
                all_chunks.extend(chunks) 
                
            elif filename.endswith(".docx"):
                print(f"Processing DOCX: {filename}...")
                extracted_pages = extract_docx_pages(file_path) # Uses your new function!
                chunks = chunk_extracted_pages(extracted_pages)
                all_chunks.extend(chunks)

        if not all_chunks:
            print("No PDF or DOCX files found in the data directory!")
        else:
            print(f"\nSaving a total of {len(all_chunks)} chunks to the database...")
            save_to_vector_db(all_chunks)
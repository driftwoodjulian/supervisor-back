import chromadb
from chromadb.utils import embedding_functions
import json
import os
import time

CHROMA_PATH = "./chroma_db"
VECTOR_COLLECTION_NAME = "victor_expert_chats"

def init_vector_store():
    # We use ChromaDB locally to ensure we don't modify the PostgreSQL DB
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    
    # Use Chroma's DefaultEmbeddingFunction (all-MiniLM-L6-v2)
    # It runs locally in Python, requires no external AI server, and is extremely fast.
    default_ef = embedding_functions.DefaultEmbeddingFunction()
    
    collection = client.get_or_create_collection(
        name=VECTOR_COLLECTION_NAME,
        embedding_function=default_ef
    )
    
    return collection

def ingest_chats(limit=1000):
    collection = init_vector_store()
    
    with open('backend/victor_chats.json', 'r', encoding='utf-8') as f:
        qa_pairs = json.load(f)
        
    print(f"Loaded {len(qa_pairs)} interactions. Ingesting top {limit} for RAG context...")
    
    # We embed the "question" (what the user asked)
    # So when a new user asks a similar question, we retrieve Victor's answer
    
    documents = []
    metadatas = []
    ids = []
    
    count = 0
    for i, pair in enumerate(qa_pairs[:limit]):
        if not pair['question'] or not pair['answer']:
            continue
            
        docs = pair['question']
        meta = {
            "answer": pair['answer'],
            "chat_id": pair['chat_id']
        }
        
        documents.append(docs)
        metadatas.append(meta)
        ids.append(f"victor_chat_{i}")
        count += 1
        
    # Batch adding to Chroma
    batch_size = 100
    for i in range(0, len(documents), batch_size):
        end = min(i + batch_size, len(documents))
        try:
            collection.add(
                documents=documents[i:end],
                metadatas=metadatas[i:end],
                ids=ids[i:end]
            )
            print(f"Added batch {end}/{count} to ChromaDB")
        except Exception as e:
            print(f"Failed embedding batch: {e}")
            
    print(f"Successfully ingested {count} interactions into {CHROMA_PATH}!")

def search_victor(query, n_results=3):
    collection = init_vector_store()
    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )
    return results

if __name__ == "__main__":
    # Test ingestion
    ingest_chats(limit=1500) # Limiting to 1500 for fast setup, can be increased later
    
    print("\nTesting semantic search...")
    res = search_victor("tengo un problema con el formulario")
    print(f"Search results for 'tengo un problema con el formulario':\\n")
    for i, (doc, meta) in enumerate(zip(res['documents'][0], res['metadatas'][0])):
        print(f"--- Result {i+1} ---")
        print(f"User Asked: {doc}")
        print(f"Victor Answered: {meta['answer']}\\n")

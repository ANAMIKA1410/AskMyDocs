"""
RAG Document Q&A System with FastAPI - FIXED VERSION
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from sentence_transformers import SentenceTransformer
import chromadb
import requests
import tempfile

# ============================================================================
# RAG SYSTEM
# ============================================================================

class RAGSystem:
    def __init__(self, api_key):
        self.api_key = api_key
        print("Loading embedding model...")
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Persistent storage - data saved to disk
        self.chroma_client = chromadb.PersistentClient(path="./chroma_db")
        self.collection = self.chroma_client.get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"}
        )
        print("✓ RAG System ready! Data stored in ./chroma_db")
    
    def chunk_text(self, text, chunk_size=200, overlap=50):
        words = text.split()
        chunks = []
        for i in range(0, len(words), chunk_size - overlap):
            chunk = ' '.join(words[i:i + chunk_size])
            if chunk:
                chunks.append(chunk)
        return chunks
    
    def load_document(self, file_path, file_name):
        print(f"Loading: {file_name}")
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        chunks = self.chunk_text(text)
        if not chunks:
            raise ValueError("Document empty")
        
        embeddings = self.embedding_model.encode(chunks).tolist()
        ids = [f"{file_name}_{i}" for i in range(len(chunks))]
        metadatas = [{"source": file_name, "chunk_id": i} for i in range(len(chunks))]
        
        self.collection.add(
            embeddings=embeddings,
            documents=chunks,
            ids=ids,
            metadatas=metadatas
        )
        print(f"✓ Loaded {len(chunks)} chunks from {file_name}")
        return len(chunks)
    
    def retrieve_context(self, query, top_k=3):
        query_embedding = self.embedding_model.encode([query]).tolist()
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=top_k
        )
        
        contexts = []
        if results['documents'] and results['documents'][0]:
            for i, doc in enumerate(results['documents'][0]):
                contexts.append({
                    'text': doc,
                    'source': results['metadatas'][0][i]['source']
                })
        return contexts
    
    def generate_answer(self, query, contexts):
        if not contexts:
            return "No documents loaded."
        
        context_text = "\n\n".join([f"[{ctx['source']}]\n{ctx['text']}" for ctx in contexts])
        
        prompt = f"""Answer based on this context:

{context_text}

Question: {query}
Answer:"""
        
        # FIXED: Added -latest to model name and using v1 endpoint
        api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={self.api_key}"
        
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }
        
        print(f"Calling Gemini API...")
        print(f"URL: {api_url[:80]}...")  # Show URL for debugging
        
        try:
            response = requests.post(
                api_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            print(f"Response Status: {response.status_code}")
            
            if response.status_code != 200:
                print(f"Error Response: {response.text}")
                return f"API Error: Status {response.status_code} - {response.text[:200]}"
            
            data = response.json()
            
            if 'candidates' in data and data['candidates']:
                answer = data['candidates'][0]['content']['parts'][0]['text']
                print("✓ Answer generated successfully")
                return answer
            
            return "No answer generated"
            
        except Exception as e:
            print(f"Exception: {str(e)}")
            return f"Error: {str(e)}"
    
    def query(self, question, top_k=3):
        print(f"\n🔍 Query: {question}")
        contexts = self.retrieve_context(question, top_k)
        
        if not contexts:
            return {
                "answer": "No documents loaded. Please upload documents first.",
                "sources": [],
                "num_chunks": 0
            }
        
        print(f"📚 Retrieved {len(contexts)} chunks")
        answer = self.generate_answer(question, contexts)
        sources = list(set(ctx['source'] for ctx in contexts))
        
        return {
            "answer": answer,
            "sources": sources,
            "num_chunks": len(contexts)
        }
    
    def reset(self):
        self.chroma_client.reset()
        self.collection = self.chroma_client.get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"}
        )
        print("✓ Database reset")
    
    def get_stats(self):
        count = self.collection.count()
        if count > 0:
            results = self.collection.get()
            sources = list(set(m['source'] for m in results['metadatas']))
            return {
                "total_chunks": count,
                "total_documents": len(sources),
                "documents": sources
            }
        return {
            "total_chunks": 0,
            "total_documents": 0,
            "documents": []
        }


# ============================================================================
# FASTAPI APPLICATION
# ============================================================================

app = FastAPI(
    title="RAG Document Q&A API",
    description="Upload documents and ask questions",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global RAG system
rag_system = None

# Gemini API Key
GEMINI_API_KEY = "AIzaSyAlZpEvkMYBfefhhXMAQ6_3v_dqSCt87XU"


# ============================================================================
# MODELS
# ============================================================================

class QueryRequest(BaseModel):
    question: str
    top_k: Optional[int] = 3

class QueryResponse(BaseModel):
    question: str
    answer: str
    sources: List[str]
    num_chunks_retrieved: int

class DocumentInfo(BaseModel):
    filename: str
    chunks: int

class StatusResponse(BaseModel):
    status: str
    message: str


# ============================================================================
# ENDPOINTS
# ============================================================================

@app.on_event("startup")
async def startup():
    global rag_system
    print("\n" + "="*70)
    print("🚀 STARTING RAG DOCUMENT Q&A API")
    print("="*70)
    rag_system = RAGSystem(GEMINI_API_KEY)
    print("="*70)
    print("✓ Server ready at http://localhost:8000")
    print("✓ API docs at http://localhost:8000/docs")
    print("="*70 + "\n")


@app.get("/")
async def root():
    return {
        "name": "RAG Document Q&A API",
        "version": "2.0.0",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "rag_initialized": rag_system is not None
    }


@app.post("/upload", response_model=DocumentInfo)
async def upload_document(file: UploadFile = File(...)):
    if not rag_system:
        raise HTTPException(status_code=500, detail="RAG not initialized")
    
    if not file.filename.endswith(('.txt', '.md')):
        raise HTTPException(status_code=400, detail="Only .txt and .md files supported")
    
    try:
        # Save to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1], mode='wb') as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        # Load into RAG
        chunks = rag_system.load_document(tmp_path, file.filename)
        os.unlink(tmp_path)
        
        return DocumentInfo(filename=file.filename, chunks=chunks)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/upload-multiple")
async def upload_multiple(files: List[UploadFile] = File(...)):
    if not rag_system:
        raise HTTPException(status_code=500, detail="RAG not initialized")
    
    results = []
    errors = []
    
    for file in files:
        if not file.filename.endswith(('.txt', '.md')):
            errors.append(f"{file.filename}: Invalid format")
            continue
        
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1], mode='wb') as tmp:
                content = await file.read()
                tmp.write(content)
                tmp_path = tmp.name
            
            chunks = rag_system.load_document(tmp_path, file.filename)
            os.unlink(tmp_path)
            
            results.append({"filename": file.filename, "chunks": chunks})
        except Exception as e:
            errors.append(f"{file.filename}: {str(e)}")
    
    return {
        "uploaded": results,
        "errors": errors,
        "total_uploaded": len(results),
        "total_errors": len(errors)
    }


@app.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    if not rag_system:
        raise HTTPException(status_code=500, detail="RAG not initialized")
    
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    try:
        result = rag_system.query(request.question, request.top_k)
        
        return QueryResponse(
            question=request.question,
            answer=result["answer"],
            sources=result["sources"],
            num_chunks_retrieved=result["num_chunks"]
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/documents")
async def list_documents():
    if not rag_system:
        raise HTTPException(status_code=500, detail="RAG not initialized")
    
    return rag_system.get_stats()


@app.post("/reset", response_model=StatusResponse)
async def reset_database():
    if not rag_system:
        raise HTTPException(status_code=500, detail="RAG not initialized")
    
    try:
        rag_system.reset()
        return StatusResponse(status="success", message="All documents cleared")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    print("\n" + "🚀"*30)
    print("Starting RAG API Server...")
    print("🚀"*30 + "\n")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

# 📚 AskMyDocs  
**Conversational AI for Your Documents**  
*Upload documents, ask questions, and get intelligent answers powered by Retrieval-Augmented Generation (RAG).*

---

## 🚀 What is AskMyDocs?
AskMyDocs is a **Streamlit-based frontend** integrated with a **FastAPI backend** that enables users to:
- Upload `.txt` or `.md` documents.
- Ask natural language questions about the content.
- Get accurate answers with sources using **RAG (Retrieval-Augmented Generation)**.

---

## 🔍 What is RAG?
**Retrieval-Augmented Generation (RAG)** is an AI technique that combines:
- **Document Retrieval**: Finds relevant chunks from your documents using embeddings.
- **Generative AI**: Uses a language model to generate answers based on retrieved context.

This approach ensures:

✅ More accurate answers  
✅ Reduced hallucinations  
✅ Context-aware responses  

---

## 🛠️ How RAG Works in This Project
1. **Upload Documents**  
   - Supported formats: `.txt`, `.md`
   - Documents are split into smaller **chunks** for better retrieval.

2. **Embedding & Storage**  
   - Each chunk is converted into a **vector embedding** using **SentenceTransformer (all-MiniLM-L6-v2)**.
   - Embeddings are stored in **ChromaDB**, a high-performance vector database.

3. **Query Process**  
   - Your question is embedded into a vector.
   - Similar chunks are retrieved from ChromaDB.
   - **Google Gemini 2.5 Flash** generates an answer using these chunks.

---

## 🧠 What is ChromaDB?
**ChromaDB** is an open-source **vector database** optimized for storing and querying embeddings.  
In AskMyDocs:
- It stores document chunks as embeddings.
- Enables fast similarity search for relevant context.

---

## 🤖 What is Generative AI?
Generative AI refers to models that **generate human-like text** based on input.  
Here, **Gemini AI**:
- Takes retrieved chunks as context.
- Produces a natural, coherent answer.

---

## 🖥️ Application Architecture
- **Frontend**: Streamlit (Interactive UI)
- **Backend**: FastAPI (API endpoints)
- **Embeddings**: SentenceTransformer
- **Vector Store**: ChromaDB
- **AI Model**: Google Gemini 2.5 Flash

---

## ✨ Features
- ✅ Upload single or multiple documents
- ✅ Ask questions in natural language
- ✅ Get answers with sources
- ✅ Adjustable `top_k` chunks for better context
- ✅ Persistent document storage

---

## 📦 Installation
```bash
# Clone the repo
gitgit clone https://github.com/ANAMIKA1410/AskMyDocs.git
cd AskMyDocs

# Install dependencies
pip install -r requirements.txt

# Start backend
python main.py

# Start frontend
python app.py

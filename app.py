# """
# Streamlit Frontend for RAG Document Q&A System
# """

# import streamlit as st
# import requests
# import json
# from typing import List

# # FastAPI Backend URL
# API_BASE_URL = "http://localhost:8000"

# # Page config
# st.set_page_config(
#     page_title="RAG Document Q&A",
#     page_icon="📚",
#     layout="wide"
# )

# # Custom CSS
# st.markdown("""
#     <style>
#     .main {
#         padding: 2rem;
#     }
#     .stButton>button {
#         width: 100%;
#     }
#     .upload-section {
#         background-color: #f0f2f6;
#         padding: 2rem;
#         border-radius: 10px;
#         margin-bottom: 2rem;
#     }
#     .stats-box {
#         background-color: #e8f4f8;
#         padding: 1rem;
#         border-radius: 5px;
#         margin: 1rem 0;
#     }
#     .answer-box {
#         background-color: #f9f9f9;
#         padding: 1.5rem;
#         border-radius: 10px;
#         border-left: 5px solid #4CAF50;
#         margin: 1rem 0;
#     }
#     .source-tag {
#         display: inline-block;
#         background-color: #2196F3;
#         color: white;
#         padding: 0.3rem 0.8rem;
#         border-radius: 15px;
#         margin: 0.2rem;
#         font-size: 0.85rem;
#     }
#     </style>
# """, unsafe_allow_html=True)

# # Helper functions
# def check_api_health():
#     """Check if FastAPI backend is running"""
#     try:
#         response = requests.get(f"{API_BASE_URL}/health", timeout=3)
#         return response.status_code == 200
#     except:
#         return False

# def upload_document(file):
#     """Upload a single document to the API"""
#     files = {"file": (file.name, file, file.type)}
#     try:
#         response = requests.post(f"{API_BASE_URL}/upload", files=files, timeout=30)
#         if response.status_code == 200:
#             return response.json()
#         else:
#             return {"error": response.text}
#     except Exception as e:
#         return {"error": str(e)}

# def upload_multiple_documents(files):
#     """Upload multiple documents to the API"""
#     files_data = [("files", (f.name, f, f.type)) for f in files]
#     try:
#         response = requests.post(f"{API_BASE_URL}/upload-multiple", files=files_data, timeout=60)
#         if response.status_code == 200:
#             return response.json()
#         else:
#             return {"error": response.text}
#     except Exception as e:
#         return {"error": str(e)}

# def query_documents(question, top_k=3):
#     """Query the documents"""
#     try:
#         response = requests.post(
#             f"{API_BASE_URL}/query",
#             json={"question": question, "top_k": top_k},
#             timeout=60
#         )
#         if response.status_code == 200:
#             return response.json()
#         else:
#             return {"error": response.text}
#     except Exception as e:
#         return {"error": str(e)}

# def get_documents_stats():
#     """Get statistics about uploaded documents"""
#     try:
#         response = requests.get(f"{API_BASE_URL}/documents", timeout=5)
#         if response.status_code == 200:
#             return response.json()
#         else:
#             return None
#     except:
#         return None

# def reset_database():
#     """Reset the database"""
#     try:
#         response = requests.post(f"{API_BASE_URL}/reset", timeout=10)
#         return response.status_code == 200
#     except:
#         return False

# # Initialize session state
# if 'chat_history' not in st.session_state:
#     st.session_state.chat_history = []

# # Main UI
# st.title("📚 RAG Document Q&A System")
# st.markdown("---")

# # Check API health
# if not check_api_health():
#     st.error("⚠️ FastAPI backend is not running! Please start the server at http://localhost:8000")
#     st.info("Run: `python main.py` to start the backend")
#     st.stop()
# else:
#     st.success("✅ Connected to FastAPI backend")

# # Sidebar
# with st.sidebar:
#     st.header("📊 System Status")
    
#     # Get stats
#     stats = get_documents_stats()
#     if stats:
#         st.markdown(f"""
#         <div class="stats-box">
#             <h3>📄 Documents: {stats['total_documents']}</h3>
#             <h3>📦 Chunks: {stats['total_chunks']}</h3>
#         </div>
#         """, unsafe_allow_html=True)
        
#         if stats['documents']:
#             st.subheader("Uploaded Files:")
#             for doc in stats['documents']:
#                 st.markdown(f"- `{doc}`")
    
#     st.markdown("---")
    
#     # Reset button
#     if st.button("🗑️ Reset Database", type="secondary"):
#         if reset_database():
#             st.success("Database reset successfully!")
#             st.session_state.chat_history = []
#             st.rerun()
#         else:
#             st.error("Failed to reset database")
    
#     st.markdown("---")
#     st.markdown("### ⚙️ Settings")
#     top_k = st.slider("Number of chunks to retrieve", 1, 10, 3)

# # Main content area with tabs
# tab1, tab2, tab3 = st.tabs(["💬 Chat", "📤 Upload Documents", "📖 About"])

# # Tab 1: Chat Interface
# with tab1:
#     st.header("Ask Questions About Your Documents")
    
#     # Display chat history
#     for chat in st.session_state.chat_history:
#         # User message
#         with st.chat_message("user"):
#             st.write(chat['question'])
        
#         # Assistant message
#         with st.chat_message("assistant"):
#             st.markdown(f"""
#             <div class="answer-box">
#                 {chat['answer']}
#             </div>
#             """, unsafe_allow_html=True)
            
#             if chat.get('sources'):
#                 st.markdown("**Sources:**")
#                 for source in chat['sources']:
#                     st.markdown(f'<span class="source-tag">{source}</span>', unsafe_allow_html=True)
            
#             st.caption(f"Retrieved {chat.get('num_chunks', 0)} chunks")
    
#     # Chat input
#     question = st.chat_input("Ask a question about your documents...")
    
#     if question:
#         # Check if documents are uploaded
#         stats = get_documents_stats()
#         if not stats or stats['total_documents'] == 0:
#             st.warning("⚠️ Please upload documents first!")
#         else:
#             # Show user message immediately
#             with st.chat_message("user"):
#                 st.write(question)
            
#             # Show loading spinner
#             with st.chat_message("assistant"):
#                 with st.spinner("Thinking..."):
#                     result = query_documents(question, top_k)
                
#                 if "error" in result:
#                     st.error(f"Error: {result['error']}")
#                 else:
#                     st.markdown(f"""
#                     <div class="answer-box">
#                         {result['answer']}
#                     </div>
#                     """, unsafe_allow_html=True)
                    
#                     if result.get('sources'):
#                         st.markdown("**Sources:**")
#                         for source in result['sources']:
#                             st.markdown(f'<span class="source-tag">{source}</span>', unsafe_allow_html=True)
                    
#                     st.caption(f"Retrieved {result.get('num_chunks_retrieved', 0)} chunks")
                    
#                     # Add to chat history
#                     st.session_state.chat_history.append({
#                         'question': question,
#                         'answer': result['answer'],
#                         'sources': result.get('sources', []),
#                         'num_chunks': result.get('num_chunks_retrieved', 0)
#                     })

# # Tab 2: Upload Documents
# with tab2:
#     st.header("Upload Documents")
    
#     col1, col2 = st.columns([2, 1])
    
#     with col1:
#         st.markdown("""
#         <div class="upload-section">
#             <h3>📄 Upload Your Documents</h3>
#             <p>Supported formats: .txt, .md</p>
#         </div>
#         """, unsafe_allow_html=True)
        
#         upload_option = st.radio("Upload option:", ["Single File", "Multiple Files"])
        
#         if upload_option == "Single File":
#             uploaded_file = st.file_uploader(
#                 "Choose a file",
#                 type=['txt', 'md'],
#                 help="Upload a .txt or .md file"
#             )
            
#             if uploaded_file:
#                 if st.button("Upload File", type="primary"):
#                     with st.spinner("Uploading and processing..."):
#                         result = upload_document(uploaded_file)
                        
#                         if "error" in result:
#                             st.error(f"Error: {result['error']}")
#                         else:
#                             st.success(f"✅ Uploaded '{result['filename']}' - {result['chunks']} chunks created")
#                             st.rerun()
        
#         else:  # Multiple Files
#             uploaded_files = st.file_uploader(
#                 "Choose files",
#                 type=['txt', 'md'],
#                 accept_multiple_files=True,
#                 help="Upload multiple .txt or .md files"
#             )
            
#             if uploaded_files:
#                 if st.button("Upload All Files", type="primary"):
#                     with st.spinner(f"Uploading {len(uploaded_files)} files..."):
#                         result = upload_multiple_documents(uploaded_files)
                        
#                         if "error" in result:
#                             st.error(f"Error: {result['error']}")
#                         else:
#                             st.success(f"✅ Uploaded {result['total_uploaded']} files successfully")
                            
#                             if result['uploaded']:
#                                 st.write("**Uploaded files:**")
#                                 for file_info in result['uploaded']:
#                                     st.write(f"- {file_info['filename']}: {file_info['chunks']} chunks")
                            
#                             if result['errors']:
#                                 st.error("**Errors:**")
#                                 for error in result['errors']:
#                                     st.write(f"- {error}")
                            
#                             st.rerun()
    
#     with col2:
#         st.info("""
#         **Tips:**
#         - Upload text or markdown files
#         - Documents are split into chunks
#         - Each chunk is embedded for search
#         - You can upload multiple files at once
#         """)

# # Tab 3: About
# with tab3:
#     st.header("About This System")
    
#     st.markdown("""
#     ### 🎯 What is RAG?
    
#     **Retrieval-Augmented Generation (RAG)** is a technique that combines:
#     - **Document Retrieval**: Finding relevant information from your documents
#     - **AI Generation**: Using AI to generate answers based on retrieved context
    
#     ### 🔧 How It Works
    
#     1. **Upload Documents**: Upload your .txt or .md files
#     2. **Chunking**: Documents are split into smaller chunks
#     3. **Embedding**: Each chunk is converted to a vector embedding
#     4. **Storage**: Embeddings are stored in ChromaDB
#     5. **Query**: When you ask a question:
#        - Your question is embedded
#        - Similar chunks are retrieved
#        - Gemini AI generates an answer using the chunks
    
#     ### 🛠️ Technology Stack
    
#     - **Backend**: FastAPI
#     - **Frontend**: Streamlit
#     - **Embeddings**: SentenceTransformer (all-MiniLM-L6-v2)
#     - **Vector Store**: ChromaDB
#     - **AI Model**: Google Gemini 2.5 Flash
    
#     ### 📝 Usage Tips
    
#     - Upload documents before asking questions
#     - Be specific in your questions
#     - Adjust the number of chunks retrieved for better context
#     - Documents persist across sessions (stored in ./chroma_db)
    
#     ### 🔗 API Endpoints
    
#     - `GET /health` - Check API health
#     - `POST /upload` - Upload single document
#     - `POST /upload-multiple` - Upload multiple documents
#     - `POST /query` - Query documents
#     - `GET /documents` - Get document statistics
#     - `POST /reset` - Reset database
    
#     ---
    
#     **Made with ❤️ using FastAPI and Streamlit**
#     """)

# # Footer
# st.markdown("---")
# st.markdown(
#     "<div style='text-align: center; color: gray;'>RAG Document Q&A System v2.0</div>",
#     unsafe_allow_html=True
# )



""" Streamlit Frontend for RAG Document Q&A System """
import streamlit as st
import requests
import json
from typing import List

# FastAPI Backend URL
API_BASE_URL = "http://localhost:8000"

# Page config
st.set_page_config(
    page_title="RAG Document Q&A",
    page_icon="📚",
    layout="wide"
)

# --- NEW/CHANGED: Custom CSS to fix chat input at bottom and make chat area scrollable ---
st.markdown(
    """
    <style>
      /* Make main container account for fixed chat input height */
      .block-container {
        padding-bottom: 7.5rem; /* space for fixed chat input */
      }

      /* Pin chat input bar to bottom */
      div[data-testid="stChatInput"] {
        position: fixed !important;
        bottom: max(12px, env(safe-area-inset-bottom));
        left: max(320px, calc(env(safe-area-inset-left)));
        right: max(12px, calc(env(safe-area-inset-right)));
        z-index: 1000;
        background: var(--background-color);
        border-radius: 12px;
        box-shadow: 0 6px 20px rgba(0,0,0,0.08);
        padding: 8px 12px;
      }

      /* When sidebar is collapsed, adjust left edge gracefully */
      @media (max-width: 1100px) {
        div[data-testid="stChatInput"] {
          left: 12px;
        }
      }

      /* Optional: compact the spacing between chat messages */
      [data-testid="stChatMessage"] {
        margin-bottom: 0.75rem;
      }

      /* Optional: style the Sources section bullets */
      .rag-sources li {
        margin: 0.25rem 0;
      }

      /* A lightweight divider under the chat header */
      .chat-header-divider {
        border-top: 1px solid var(--secondary-background-color);
        margin-top: 0.5rem;
        margin-bottom: 0.75rem;
      }
    </style>
    """,
    unsafe_allow_html=True
)

# Helper functions
def check_api_health():
    """Check if FastAPI backend is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=3)
        return response.status_code == 200
    except:
        return False

def upload_document(file):
    """Upload a single document to the API"""
    files = {"file": (file.name, file, file.type)}
    try:
        response = requests.post(f"{API_BASE_URL}/upload", files=files, timeout=30)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": response.text}
    except Exception as e:
        return {"error": str(e)}

def upload_multiple_documents(files):
    """Upload multiple documents to the API"""
    files_data = [("files", (f.name, f, f.type)) for f in files]
    try:
        response = requests.post(f"{API_BASE_URL}/upload-multiple", files=files_data, timeout=60)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": response.text}
    except Exception as e:
        return {"error": str(e)}

def query_documents(question, top_k=3):
    """Query the documents"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/query",
            json={"question": question, "top_k": top_k},
            timeout=60
        )
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": response.text}
    except Exception as e:
        return {"error": str(e)}

def get_documents_stats():
    """Get statistics about uploaded documents"""
    try:
        response = requests.get(f"{API_BASE_URL}/documents", timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except:
        return None

def reset_database():
    """Reset the database"""
    try:
        response = requests.post(f"{API_BASE_URL}/reset", timeout=10)
        return response.status_code == 200
    except:
        return False

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Main UI
st.title("📚 RAG Document Q&A System")
st.markdown("---")

# Check API health
if not check_api_health():
    st.error("⚠️ FastAPI backend is not running! Please start the server at http://localhost:8000")
    st.info("Run: `python main.py` to start the backend")
    st.stop()
else:
    st.success("✅ Connected to FastAPI backend")

# Sidebar
with st.sidebar:
    st.header("📈 System Status")
    stats = get_documents_stats()
    if stats:
        st.markdown(f"""
#### 📄 Documents: {stats['total_documents']}
#### 📦 Chunks: {stats['total_chunks']}
        """, unsafe_allow_html=True)
        if stats['documents']:
            st.subheader("Uploaded Files:")
            for doc in stats['documents']:
                st.markdown(f"- `{doc}`")
    st.markdown("---")
    if st.button("🗑️ Reset Database", type="secondary"):
        if reset_database():
            st.success("Database reset successfully!")
            st.session_state.chat_history = []
            st.rerun()
        else:
            st.error("Failed to reset database")
    st.markdown("---")
    st.markdown("### ⚙️ Settings")
    top_k = st.slider("Number of chunks to retrieve", 1, 10, 3)

# Tabs
tab1, tab2, tab3 = st.tabs(["💬 Chat", "📤 Upload Documents", "📖 About"])

# Tab 1: Chat Interface
with tab1:
    st.header("Ask Questions About Your Documents")
    st.markdown('<div class="chat-header-divider"></div>', unsafe_allow_html=True)

    # --- NEW/CHANGED: Create a dedicated container for messages ---
    chat_container = st.container()

    # Render chat history (top to bottom)
    with chat_container:
        for chat in st.session_state.chat_history:
            with st.chat_message("user"):
                st.write(chat['question'])
            with st.chat_message("assistant"):
                st.markdown(f"{chat['answer']}", unsafe_allow_html=True)
                if chat.get('sources'):
                    st.markdown("**Sources:**")
                    # Make sources into a compact list
                    st.markdown("<ul class='rag-sources'>" + "".join(
                        [f"<li>{source}</li>" for source in chat['sources']]
                    ) + "</ul>", unsafe_allow_html=True)
                st.caption(f"Retrieved {chat.get('num_chunks', 0)} chunks")

    # --- NEW/CHANGED: Place chat input AFTER messages; CSS pins it to bottom ---
    question = st.chat_input("Ask a question about your documents...")
    if question:
        # Ensure documents exist
        stats = get_documents_stats()
        if not stats or stats['total_documents'] == 0:
            st.warning("⚠️ Please upload documents first!")
        else:
            # Show user message immediately in the container
            with chat_container:
                with st.chat_message("user"):
                    st.write(question)
                with st.chat_message("assistant"):
                    with st.spinner("Thinking..."):
                        result = query_documents(question, top_k)

                        if "error" in result:
                            st.error(f"Error: {result['error']}")
                        else:
                            st.markdown(f"{result['answer']}", unsafe_allow_html=True)
                            if result.get('sources'):
                                st.markdown("**Sources:**")
                                st.markdown("<ul class='rag-sources'>" + "".join(
                                    [f"<li>{source}</li>" for source in result['sources']]
                                ) + "</ul>", unsafe_allow_html=True)
                            st.caption(f"Retrieved {result.get('num_chunks_retrieved', 0)} chunks")

            # Update chat history and re-render
            if "error" not in result:
                st.session_state.chat_history.append({
                    'question': question,
                    'answer': result['answer'],
                    'sources': result.get('sources', []),
                    'num_chunks': result.get('num_chunks_retrieved', 0)
                })

# Tab 2: Upload Documents
with tab2:
    st.header("Upload Documents")
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("""
#### 📄 Upload Your Documents

Supported formats: .txt, .md
        """, unsafe_allow_html=True)
        upload_option = st.radio("Upload option:", ["Single File", "Multiple Files"])
        if upload_option == "Single File":
            uploaded_file = st.file_uploader(
                "Choose a file",
                type=['txt', 'md'],
                help="Upload a .txt or .md file"
            )
            if uploaded_file:
                if st.button("Upload File", type="primary"):
                    with st.spinner("Uploading and processing..."):
                        result = upload_document(uploaded_file)
                        if "error" in result:
                            st.error(f"Error: {result['error']}")
                        else:
                            st.success(f"✅ Uploaded '{result['filename']}' - {result['chunks']} chunks created")
                            st.rerun()
        else:
            uploaded_files = st.file_uploader(
                "Choose files",
                type=['txt', 'md'],
                accept_multiple_files=True,
                help="Upload multiple .txt or .md files"
            )
            if uploaded_files:
                if st.button("Upload All Files", type="primary"):
                    with st.spinner(f"Uploading {len(uploaded_files)} files..."):
                        result = upload_multiple_documents(uploaded_files)
                        if "error" in result:
                            st.error(f"Error: {result['error']}")
                        else:
                            st.success(f"✅ Uploaded {result['total_uploaded']} files successfully")
                            if result['uploaded']:
                                st.write("**Uploaded files:**")
                                for file_info in result['uploaded']:
                                    st.write(f"- {file_info['filename']}: {file_info['chunks']} chunks")
                            if result['errors']:
                                st.error("**Errors:**")
                                for error in result['errors']:
                                    st.write(f"- {error}")
                            st.rerun()
    with col2:
        st.info("""
**Tips:**
- Upload text or markdown files
- Documents are split into chunks
- Each chunk is embedded for search
- You can upload multiple files at once
        """)

# Tab 3: About
with tab3:
    st.header("About This System")
    st.markdown("""
### 🎯 What is RAG?
**Retrieval-Augmented Generation (RAG)** combines:
- **Document Retrieval**: Finding relevant information from your documents
- **AI Generation**: Using AI to generate answers based on retrieved context

### 🔧 How It Works
1. **Upload Documents**: Upload your .txt or .md files
2. **Chunking**: Documents are split into smaller chunks
3. **Embedding**: Each chunk is converted to a vector embedding
4. **Storage**: Embeddings are stored in ChromaDB
5. **Query**: When you ask a question:
   - Your question is embedded
   - Similar chunks are retrieved
   - Gemini AI generates an answer using the chunks

### 🛠️ Technology Stack
- **Backend**: FastAPI
- **Frontend**: Streamlit
- **Embeddings**: SentenceTransformer (all-MiniLM-L6-v2)
- **Vector Store**: ChromaDB
- **AI Model**: Google Gemini 2.5 Flash

### 📝 Usage Tips
- Upload documents before asking questions
- Be specific in your questions
- Adjust the number of chunks retrieved for better context
- Documents persist across sessions (stored in ./chroma_db)

### 🔗 API Endpoints
- `POST /upload` - Upload single document
- `POST /upload-multiple` - Upload multiple documents
- `POST /query` - Query documents
- `GET /documents` - Get document statistics
- `POST /reset` - Reset database

---
**Made with ❤️ using FastAPI and Streamlit by Anamika Jain**
    """)
# Footer
st.markdown("---")
# st.markdown(
#     "RAG Document Q&A System v2.0", unsafe_allow    unsafe_allow_html=True




st.markdown(
    "<div style='text-align: center; color: gray;'>RAG Document Q&A System made by Anamika Jain</div>",
    unsafe_allow_html=True
)
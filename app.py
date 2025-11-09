"""
Production-Grade RAG Chatbot with Streamlit
Multi-user file upload + query interface with session management
"""
import streamlit as st
import logging
from pathlib import Path
from datetime import datetime

from config import config
from services import DocumentService, RAGService, SessionService
from src.query_classifier import QueryClassifier

# Configure page
st.set_page_config(
    page_title="RAG Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format=config.LOG_FORMAT
)
logger = logging.getLogger(__name__)


# ==================== CACHED RESOURCES ====================

@st.cache_resource
def initialize_services():
    """Initialize services once and cache"""
    try:
        doc_service = DocumentService()
        rag_service = RAGService()
        session_service = SessionService()

        # Validate configuration
        is_valid, error = config.validate()
        if not is_valid:
            st.error(f"Configuration error: {error}")
            st.stop()

        logger.info("Services initialized successfully")
        return doc_service, rag_service, session_service

    except Exception as e:
        logger.error(f"Failed to initialize services: {e}", exc_info=True)
        st.error(f"System initialization failed: {e}")
        st.stop()


doc_service, rag_service, session_service = initialize_services()

# Initialize query classifier for routing
query_classifier = QueryClassifier()

# ==================== SESSION MANAGEMENT ====================

def init_session_state():
    """Initialize Streamlit session state"""
    if "session_id" not in st.session_state:
        st.session_state.session_id = session_service.create_session()
        logger.info(f"New user session: {st.session_state.session_id}")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "uploaded_files_info" not in st.session_state:
        st.session_state.uploaded_files_info = []

    if "processing_status" not in st.session_state:
        st.session_state.processing_status = None


init_session_state()

# Get current session
session_id = st.session_state.session_id
session_data = session_service.get_session(session_id)
collection_name = session_service.get_collection_name(session_id) if config.USE_SESSION_COLLECTIONS else "pdf_documents"


# ==================== UI LAYOUT ====================

# Sidebar
with st.sidebar:
    st.title("🤖 AI Assistant")
    st.caption("💬 Chat mode + 🔍 Document search")
    st.markdown("---")

    # File Upload Section
    st.header("📄 Upload Documents")

    uploaded_file = st.file_uploader(
        "Upload PDF, TXT, or DOCX",
        type=["pdf", "txt", "docx"],
        help=f"Max size: {config.MAX_FILE_SIZE_MB}MB",
        key="file_uploader"
    )

    if uploaded_file:
        if st.button("🚀 Process Document", type="primary", use_container_width=True):
            with st.spinner("Processing document..."):
                # Save file
                file_path, error = doc_service.save_uploaded_file(
                    uploaded_file,
                    uploaded_file.name,
                    session_id
                )

                if error:
                    st.error(f"Upload failed: {error}")
                else:
                    # Process document
                    progress_bar = st.progress(0, text="Extracting text...")

                    progress_bar.progress(33, text="Generating embeddings...")
                    doc_count, error = rag_service.process_document(
                        file_path,
                        collection_name
                    )

                    if error:
                        st.error(f"Processing failed: {error}")
                    else:
                        progress_bar.progress(100, text="Complete!")

                        # Update session
                        session_service.add_file_to_session(
                            session_id,
                            uploaded_file.name,
                            doc_count
                        )

                        # Track uploaded file
                        st.session_state.uploaded_files_info.append({
                            "filename": uploaded_file.name,
                            "chunks": doc_count,
                            "uploaded_at": datetime.now().strftime("%H:%M:%S")
                        })

                        st.success(f"✅ Processed {doc_count} chunks from {uploaded_file.name}")
                        st.rerun()

    st.markdown("---")

    # Uploaded Files Display
    st.header("📚 Loaded Documents")

    if st.session_state.uploaded_files_info:
        for file_info in st.session_state.uploaded_files_info:
            with st.expander(f"📄 {file_info['filename']}", expanded=False):
                st.write(f"**Chunks:** {file_info['chunks']}")
                st.write(f"**Time:** {file_info['uploaded_at']}")
    else:
        st.info("No documents uploaded yet")

    st.markdown("---")

    # Session Stats
    if session_data:
        stats = session_service.get_session_stats(session_id)
        st.header("📊 Session Stats")
        st.metric("Documents", stats["document_count"])
        st.metric("Queries", stats["query_count"])

    # Clear Session Button
    if st.button("🗑️ Clear Session", use_container_width=True):
        # Clear vector store collection if using session collections
        if config.USE_SESSION_COLLECTIONS:
            rag_service.delete_collection(collection_name)

        # Clear uploaded files
        doc_service.cleanup_session_files(session_id)

        # Reset session state
        st.session_state.messages = []
        st.session_state.uploaded_files_info = []

        # Create new session
        st.session_state.session_id = session_service.create_session()

        st.success("Session cleared!")
        st.rerun()

    # System Info (collapsible)
    with st.expander("⚙️ System Info", expanded=False):
        st.write(f"**Model:** {config.GEMINI_MODEL}")
        st.write(f"**Embedding:** {config.EMBEDDING_MODEL}")
        st.write(f"**Top-K:** {config.TOP_K_RESULTS}")
        st.write(f"**Chunk Size:** {config.CHUNK_SIZE}")

        # Health check
        if st.button("Run Health Check"):
            health = rag_service.health_check()
            for component, status in health.items():
                st.write(f"{component}: {'✅' if status else '❌'}")


# ==================== MAIN CHAT INTERFACE ====================

st.title("💬 Chat & Document Q&A")
st.caption("🤖 Intelligent AI assistant - automatically switches between chat and document search")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        # Display sources if available
        if message["role"] == "assistant" and "sources" in message:
            if message["sources"]:
                with st.expander("📎 Sources", expanded=False):
                    for i, source in enumerate(message["sources"], 1):
                        st.markdown(f"""
                        **Source {i}** (Similarity: {source.get('similarity', 0):.2%})
                        - **File:** {source.get('source_file', 'Unknown')}
                        - **Page:** {source.get('page', 'N/A')}

                        *{source.get('content', '')[:200]}...*
                        """)

# Chat input
if prompt := st.chat_input("Ask me anything or search your documents..."):
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    st.session_state.messages.append({"role": "user", "content": prompt})

    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            # Automatically classify query to determine routing
            use_rag = query_classifier.should_use_rag(prompt)

            # Check if RAG requested but no documents uploaded
            if use_rag and not st.session_state.uploaded_files_info and config.USE_SESSION_COLLECTIONS:
                answer = "⚠️ I detected you want to search documents, but no documents are uploaded yet. Please upload a PDF first, or rephrase your question for general chat!"
                sources = []
                result = {"mode": "llm"}
            elif use_rag:
                # Use RAG pipeline - search in documents
                result = rag_service.query(
                    question=prompt,
                    collection_name=collection_name,
                    top_k=config.TOP_K_RESULTS
                )

                if result["error"]:
                    answer = f"❌ Error: {result['error']}"
                    sources = []
                elif not result["answer"]:
                    answer = "I couldn't find relevant information in the uploaded documents to answer this question."
                    sources = []
                else:
                    answer = result["answer"]
                    sources = result["sources"]
            else:
                # Use direct LLM - normal conversational AI
                result = rag_service.chat(question=prompt)

                if result["error"]:
                    answer = f"❌ Error: {result['error']}"
                elif not result["answer"]:
                    answer = "I couldn't generate a response."
                else:
                    answer = result["answer"]
                sources = []

            # Update query count
            session_service.increment_query_count(session_id)

            # Display answer
            st.markdown(answer)

            # Display mode indicator (subtle)
            mode_emoji = "🔍" if result.get("mode") == "rag" else "💬"
            mode_text = "Document Search" if result.get("mode") == "rag" else "General Chat"
            st.caption(f"{mode_emoji} {mode_text}")

            # Display sources (only for RAG)
            if sources:
                with st.expander("📎 Sources", expanded=False):
                    for i, source in enumerate(sources, 1):
                        st.markdown(f"""
                        **Source {i}** (Similarity: {source.get('similarity', 0):.2%})
                        - **File:** {source.get('source_file', 'Unknown')}
                        - **Page:** {source.get('page', 'N/A')}

                        *{source.get('content', '')[:200]}...*
                        """)

    # Save assistant message
    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "sources": sources
    })


# ==================== FOOTER ====================

st.markdown("---")
st.markdown(
    f"""
    <div style='text-align: center; color: gray; font-size: 0.8em;'>
    🤖 Powered by {config.GEMINI_MODEL} | Built with Streamlit & ChromaDB
    </div>
    """,
    unsafe_allow_html=True
)

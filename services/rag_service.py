"""
RAG Service - Orchestrates document processing and query pipeline
Integrates with existing RAG modules with production-grade error handling
"""
import logging
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import traceback
import numpy as np

from config import config
from src import (
    PDFDocumentLoader,
    EmbeddingManager,
    VectorStore,
    RAGRetriever,
    GeminiLLM,
    RAGPipeline
)

logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format=config.LOG_FORMAT
)
logger = logging.getLogger(__name__)


class RAGService:
    """High-level service for RAG operations"""

    def __init__(self):
        """Initialize RAG components"""
        try:
            # Initialize components (cached for performance)
            self.embedding_manager = EmbeddingManager(model_name=config.EMBEDDING_MODEL)
            self.llm = GeminiLLM(
                model_name=config.GEMINI_MODEL,
                api_key=config.GEMINI_API_KEY,
                temperature=config.LLM_TEMPERATURE,
                max_output_tokens=config.LLM_MAX_TOKENS
            )

            logger.info("RAG Service initialized successfully")
            logger.info(f"Config: {config.get_summary()}")

        except Exception as e:
            logger.error(f"Failed to initialize RAG Service: {e}", exc_info=True)
            raise

    def _load_document_by_type(self, file_path: Path):
        """
        Load document based on file extension

        Args:
            file_path: Path to document file

        Returns:
            List of LangChain Document objects

        Raises:
            ValueError: If file type is not supported
        """
        from langchain_community.document_loaders import (
            PyPDFLoader,
            TextLoader,
            Docx2txtLoader
        )

        suffix = file_path.suffix.lower()

        try:
            if suffix == '.pdf':
                logger.info(f"Loading PDF file: {file_path.name}")
                loader = PyPDFLoader(str(file_path))
            elif suffix == '.txt':
                logger.info(f"Loading TXT file: {file_path.name}")
                loader = TextLoader(str(file_path), encoding='utf-8')
            elif suffix == '.docx':
                logger.info(f"Loading DOCX file: {file_path.name}")
                loader = Docx2txtLoader(str(file_path))
            else:
                raise ValueError(f"Unsupported file type: {suffix}. Supported types: .pdf, .txt, .docx")

            return loader.load()

        except Exception as e:
            logger.error(f"Error loading {suffix} file: {e}", exc_info=True)
            raise

    def process_document(
        self,
        file_path: Path,
        collection_name: str = "pdf_documents"
    ) -> Tuple[Optional[int], Optional[str]]:
        """
        Process a document and add to vector store

        Args:
            file_path: Path to document file
            collection_name: ChromaDB collection name

        Returns:
            (document_count, error_message)
        """
        try:
            logger.info(f"Processing document: {file_path.name}")

            # Step 1: Load document based on file type
            from langchain_text_splitters import RecursiveCharacterTextSplitter

            # Load document using appropriate loader for file type
            raw_documents = self._load_document_by_type(file_path)

            if not raw_documents:
                return None, f"No content extracted from {file_path.suffix}. The file may be empty, corrupted, or image-based."

            logger.info(f"Loaded {len(raw_documents)} pages/sections from {file_path.name}")

            # Add source metadata
            for doc in raw_documents:
                doc.metadata['source_file'] = file_path.name
                doc.metadata['file_type'] = file_path.suffix[1:]  # pdf, txt, etc.

            # Split into chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=config.CHUNK_SIZE,
                chunk_overlap=config.CHUNK_OVERLAP,
                length_function=len,
                separators=["\n\n", "\n", " ", ""]
            )

            documents = text_splitter.split_documents(raw_documents)

            if not documents:
                return None, "Document loaded but no text chunks created after splitting"

            logger.info(f"Split into {len(documents)} chunks from {file_path.name}")

            # Step 2: Generate embeddings
            texts = [doc.page_content for doc in documents]
            metadata = [doc.metadata for doc in documents]

            embeddings = self.embedding_manager.generate_embeddings(texts)
            logger.info(f"Generated {len(embeddings)} embeddings")

            # Step 3: Store in ChromaDB
            vector_store = VectorStore(
                collection_name=collection_name,
                persist_directory=str(config.VECTOR_STORE_DIR)
            )

            # VectorStore.add_documents expects (documents, embeddings)
            # documents are already LangChain Document objects from text_splitter
            vector_store.add_documents(
                documents=documents,
                embeddings=np.array(embeddings)
            )

            logger.info(f"Successfully indexed {len(documents)} chunks to collection '{collection_name}'")

            return len(documents), None

        except FileNotFoundError:
            error_msg = f"File not found: {file_path}"
            logger.error(error_msg)
            return None, error_msg

        except Exception as e:
            error_msg = f"Error processing document: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return None, error_msg

    def query(
        self,
        question: str,
        collection_name: str = "pdf_documents",
        top_k: int = None
    ) -> Dict:
        """
        Query the RAG system

        Args:
            question: User query
            collection_name: ChromaDB collection to search
            top_k: Number of results to retrieve (default from config)

        Returns:
            {
                "answer": str,
                "sources": List[dict],
                "context_used": str,
                "error": Optional[str]
            }
        """
        try:
            if not question or not question.strip():
                return {
                    "answer": None,
                    "sources": [],
                    "context_used": "",
                    "error": "Question cannot be empty"
                }

            top_k = top_k or config.TOP_K_RESULTS

            logger.info(f"Processing query: '{question[:50]}...' (collection: {collection_name})")

            # Initialize RAG pipeline
            vector_store = VectorStore(
                collection_name=collection_name,
                persist_directory=str(config.VECTOR_STORE_DIR)
            )

            retriever = RAGRetriever(
                vector_store=vector_store,
                embedding_manager=self.embedding_manager
            )

            pipeline = RAGPipeline(
                retriever=retriever,
                llm=self.llm
            )

            # Execute query - RAGPipeline has 'answer' method, not 'query'
            result = pipeline.answer(question, top_k=top_k)

            logger.info(f"Query completed. Found {len(result.get('sources', []))} sources")

            return {
                "answer": result.get("answer"),
                "sources": result.get("sources", []),
                "context_used": result.get("context_used", ""),  # Fixed: was "context"
                "error": None,
                "mode": "rag"
            }

        except Exception as e:
            error_msg = f"Error during query: {str(e)}"
            logger.error(error_msg, exc_info=True)
            logger.error(traceback.format_exc())

            return {
                "answer": None,
                "sources": [],
                "context_used": "",
                "error": error_msg,
                "mode": "rag"
            }

    def get_collection_stats(self, collection_name: str) -> Optional[Dict]:
        """Get statistics for a collection"""
        try:
            vector_store = VectorStore(
                collection_name=collection_name,
                persist_directory=str(config.VECTOR_STORE_DIR)
            )

            stats = vector_store.get_collection_stats()
            return stats

        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return None

    def delete_collection(self, collection_name: str) -> bool:
        """Delete a collection from ChromaDB"""
        try:
            vector_store = VectorStore(
                collection_name=collection_name,
                persist_directory=str(config.VECTOR_STORE_DIR)
            )

            vector_store.clear_collection()
            logger.info(f"Collection deleted: {collection_name}")
            return True

        except Exception as e:
            logger.error(f"Error deleting collection: {e}")
            return False

    def health_check(self) -> Dict[str, bool]:
        """Check if all components are working"""
        health = {
            "embedding_manager": False,
            "llm": False,
            "vector_store": False,
            "overall": False
        }

        try:
            # Test embedding
            test_embedding = self.embedding_manager.generate_embeddings(["test"])
            health["embedding_manager"] = len(test_embedding) > 0

            # Test LLM - GeminiLLM has 'generate' method, not 'generate_response'
            test_response = self.llm.generate("test prompt")
            health["llm"] = test_response is not None

            # Test vector store
            vector_store = VectorStore(
                collection_name="pdf_documents",
                persist_directory=str(config.VECTOR_STORE_DIR)
            )
            stats = vector_store.get_collection_stats()
            health["vector_store"] = stats is not None

            health["overall"] = all([
                health["embedding_manager"],
                health["llm"],
                health["vector_store"]
            ])

        except Exception as e:
            logger.error(f"Health check failed: {e}")

        return health

    def chat(self, question: str) -> Dict:
        """
        Direct LLM chat without RAG (normal conversational AI)

        Args:
            question: User's question

        Returns:
            {
                "answer": str,
                "sources": [],
                "context_used": "",
                "error": Optional[str],
                "mode": "llm"
            }
        """
        try:
            logger.info(f"Direct LLM chat: '{question[:50]}...'")

            # Smart date context: Only provide date for time-specific queries
            # This prevents hallucinations when asking about recent events
            from datetime import datetime

            question_lower = question.lower()
            time_keywords = [
                "today", "date", "what day", "current date", "what's the date",
                "time", "now", "current time"
            ]

            # Check if question is asking about current date/time
            is_time_query = any(keyword in question_lower for keyword in time_keywords)

            if is_time_query:
                # Provide date context for time-specific questions
                current_date = datetime.now().strftime("%A, %B %d, %Y")
                prompt = f"""Current date: {current_date}

{question}"""
            else:
                # No date context - let Gemini answer from its knowledge base
                # This prevents hallucinations about recent events
                prompt = question

            answer = self.llm.generate(prompt)

            return {
                "answer": answer,
                "sources": [],
                "context_used": "",
                "error": None,
                "mode": "llm"
            }

        except Exception as e:
            error_msg = f"Error during chat: {str(e)}"
            logger.error(error_msg, exc_info=True)

            return {
                "answer": None,
                "sources": [],
                "context_used": "",
                "error": error_msg,
                "mode": "llm"
            }

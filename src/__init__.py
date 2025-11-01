"""
RAG Pipeline Package

A modular Retrieval-Augmented Generation (RAG) pipeline using:
- LangChain for PDF processing
- Sentence Transformers for embeddings
- ChromaDB for vector storage
- Google Gemini for answer generation
"""

from .data_loader import PDFDocumentLoader
from .embedding import EmbeddingManager
from .vectorstore import VectorStore
from .search import RAGRetriever
from .llm import GeminiLLM
from .rag_pipeline import RAGPipeline

__version__ = "1.0.0"

__all__ = [
    "PDFDocumentLoader",
    "EmbeddingManager",
    "VectorStore",
    "RAGRetriever",
    "GeminiLLM",
    "RAGPipeline",
]

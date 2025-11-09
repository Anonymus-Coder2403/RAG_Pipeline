"""
Vector Store Module

This module manages document embeddings in a ChromaDB vector store.
"""

import os
import uuid
import logging
from typing import List, Any, Dict
import numpy as np
import chromadb

logger = logging.getLogger(__name__)


class VectorStore:
    """Manages document embeddings in a ChromaDB vector store"""

    def __init__(
        self,
        collection_name: str = "pdf_documents",
        persist_directory: str = None
    ):
        """
        Initialize the vector store

        Args:
            collection_name: Name of the ChromaDB collection
            persist_directory: Directory to persist the vector store (uses config default if None)
        """
        # Import config only when needed to avoid circular dependencies
        if persist_directory is None:
            from config import config
            persist_directory = str(config.VECTOR_STORE_DIR)

        self.collection_name = collection_name
        self.persist_directory = persist_directory
        self.client = None
        self.collection = None
        self._initialize_store()

    def _initialize_store(self):
        """Initialize ChromaDB client and collection"""
        try:
            # Create persistent ChromaDB client
            os.makedirs(self.persist_directory, exist_ok=True)
            self.client = chromadb.PersistentClient(path=self.persist_directory)

            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": "PDF document embeddings for RAG"}
            )
            logger.info(f"Vector store initialized. Collection: {self.collection_name}")
            logger.info(f"Existing documents in collection: {self.collection.count()}")

        except Exception as e:
            logger.error(f"Error initializing vector store: {e}", exc_info=True)
            raise

    def add_documents(self, documents: List[Any], embeddings: np.ndarray):
        """
        Add documents and their embeddings to the vector store

        Args:
            documents: List of LangChain documents
            embeddings: Corresponding embeddings for the documents
        """
        if len(documents) != len(embeddings):
            raise ValueError("Number of documents must match number of embeddings")

        logger.info(f"Adding {len(documents)} documents to vector store...")

        # Prepare data for ChromaDB
        ids = []
        metadatas = []
        documents_text = []
        embeddings_list = []

        for i, (doc, embedding) in enumerate(zip(documents, embeddings)):
            # Generate unique ID
            doc_id = f"doc_{uuid.uuid4().hex[:8]}_{i}"
            ids.append(doc_id)

            # Prepare metadata
            metadata = dict(doc.metadata)
            metadata['doc_index'] = i
            metadata['content_length'] = len(doc.page_content)
            metadatas.append(metadata)

            # Document content
            documents_text.append(doc.page_content)

            # Embedding
            embeddings_list.append(embedding.tolist())

        # Add to collection
        try:
            self.collection.add(
                ids=ids,
                embeddings=embeddings_list,
                metadatas=metadatas,
                documents=documents_text
            )
            logger.info(f"Successfully added {len(documents)} documents to vector store")
            logger.info(f"Total documents in collection: {self.collection.count()}")

        except Exception as e:
            logger.error(f"Error adding documents to vector store: {e}", exc_info=True)
            raise

    def get_collection_stats(self) -> dict:
        """
        Get statistics about the collection

        Returns:
            Dictionary with collection statistics
        """
        return {
            "name": self.collection_name,
            "count": self.collection.count(),
            "metadata": self.collection.metadata
        }

    def query(self, query_embeddings: List[List[float]], n_results: int = 5) -> Dict:
        """
        Query the collection for similar documents

        Args:
            query_embeddings: List of query embedding vectors
            n_results: Number of results to return

        Returns:
            Query results with documents, metadatas, distances, ids
        """
        try:
            return self.collection.query(
                query_embeddings=query_embeddings,
                n_results=n_results
            )
        except Exception as e:
            logger.error(f"Error querying vector store: {e}", exc_info=True)
            raise

    def clear_collection(self):
        """Delete all documents from the collection"""
        try:
            self.client.delete_collection(self.collection_name)
            logger.info(f"Deleted collection: {self.collection_name}")
            # Recreate empty collection
            self._initialize_store()
        except Exception as e:
            logger.error(f"Error clearing collection: {e}", exc_info=True)
            raise

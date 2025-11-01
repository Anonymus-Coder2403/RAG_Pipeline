"""
PDF Document Loader Module

This module handles loading and processing PDF documents for the RAG pipeline.
"""

import os
from pathlib import Path
from typing import List, Any
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


class PDFDocumentLoader:
    """Handles loading and chunking PDF documents"""

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        separators: List[str] = None
    ):
        """
        Initialize the PDF document loader

        Args:
            chunk_size: Maximum size of each text chunk
            chunk_overlap: Number of characters to overlap between chunks
            separators: List of separators for text splitting
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators or ["\n\n", "\n", " ", ""]

        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=self.separators
        )

    def load_pdfs(self, pdf_directory: str) -> List[Any]:
        """
        Load all PDF files from a directory

        Args:
            pdf_directory: Path to directory containing PDF files

        Returns:
            List of LangChain Document objects
        """
        all_documents = []
        pdf_dir = Path(pdf_directory)

        # Find all PDF files recursively
        pdf_files = list(pdf_dir.glob("**/*.pdf"))

        print(f"Found {len(pdf_files)} PDF files to process")

        for pdf_file in pdf_files:
            print(f"\nProcessing: {pdf_file.name}")
            try:
                loader = PyPDFLoader(str(pdf_file))
                documents = loader.load()

                # Add source information to metadata
                for doc in documents:
                    doc.metadata['source_file'] = pdf_file.name
                    doc.metadata['file_type'] = 'pdf'

                all_documents.extend(documents)
                print(f"  ✓ Loaded {len(documents)} pages")

            except Exception as e:
                print(f"  ✗ Error: {e}")

        print(f"\nTotal documents loaded: {len(all_documents)}")
        return all_documents

    def split_documents(self, documents: List[Any]) -> List[Any]:
        """
        Split documents into smaller chunks

        Args:
            documents: List of LangChain Document objects

        Returns:
            List of chunked Document objects
        """
        split_docs = self.text_splitter.split_documents(documents)
        print(f"Split {len(documents)} documents into {len(split_docs)} chunks")

        if split_docs:
            print(f"\nExample chunk:")
            print(f"Content: {split_docs[0].page_content[:200]}...")
            print(f"Metadata: {split_docs[0].metadata}")

        return split_docs

    def load_and_split(self, pdf_directory: str) -> List[Any]:
        """
        Load PDFs and split them into chunks in one step

        Args:
            pdf_directory: Path to directory containing PDF files

        Returns:
            List of chunked Document objects
        """
        documents = self.load_pdfs(pdf_directory)
        return self.split_documents(documents)

# 🚀 RAG Pipeline Project Documentation

## 📁 Project Structure
```
RAG/
├── data/
│   ├── pdf/                  # PDF documents for processing
│   ├── text_files/          # Sample ML/DL content
│   └── vector_store/        # ChromaDB persistence
├── notebook/
│   ├── document.ipynb       # Text ingestion examples
│   └── pdf_loader.ipynb     # Core RAG pipeline
├── requirements.txt
└── README.md
```

## 🎯 Project Overview
This project implements a **Retrieval-Augmented Generation (RAG)** pipeline that:
- Processes PDF and text documents
- Generates semantic embeddings
- Enables similarity-based retrieval
- Supports LLM augmentation with custom knowledge

## 🔑 Key Components

### 1️⃣ Document Processing (`pdf_loader.ipynb`)
```python
def process_all_pdfs(pdf_directory):
    """Process PDFs recursively, extract text, add metadata"""
    # Supports both PyPDFLoader and PyMuPDFLoader
    # Returns list of LangChain Document objects
```

### 2️⃣ Text Chunking
```python
def split_documents(documents, chunk_size=1000, chunk_overlap=200):
    """Split documents into overlapping chunks"""
    # Uses RecursiveCharacterTextSplitter
    # Maintains document metadata
```

### 3️⃣ Embedding Generation
```python
class EmbeddingManager:
    """Generate embeddings using sentence-transformers"""
    # Default model: all-MiniLM-L6-v2
    # Embedding dimension: 384
```

### 4️⃣ Vector Storage
```python
class VectorStore:
    """ChromaDB persistence layer"""
    # Persistent storage in data/vector_store
    # Supports add_documents() and query()
```

### 5️⃣ Retrieval Pipeline
```python
class RAGRetriever:
    """Semantic search with similarity scoring"""
    # Converts query to embedding
    # Returns top-k similar chunks
```

## 💻 Implementation Details

### Performance Characteristics
- **Chunking**: ~800 new chars/chunk (1000 size, 200 overlap)
- **Embedding**: 384-dimensional vectors (1.5KB per chunk)
- **Storage**: ChromaDB SQLite backend + binary indexes
- **Query Time**: O(log n) with approximate nearest neighbors

### Hardware Requirements
- RAM: 16GB recommended (scales with document count)
- GPU: Optional, supports CUDA for faster embedding
- Storage: Scales linearly with document count (~1.5KB/chunk)

## 🔧 Usage Examples

### Basic Document Processing
```python
# Load and chunk PDFs
documents = process_all_pdfs("../data/pdf")
chunks = split_documents(documents)

# Generate embeddings
embedding_manager = EmbeddingManager()
embeddings = embedding_manager.generate_embeddings([c.page_content for c in chunks])

# Store vectors
vectorstore = VectorStore()
vectorstore.add_documents(chunks, embeddings)
```

### Semantic Search
```python
# Initialize retriever
retriever = RAGRetriever(vectorstore, embedding_manager)

# Query knowledge base
results = retriever.retrieve(
    query="What is RAG?",
    top_k=5,
    score_threshold=0.7
)
```

## 📊 Current Limitations & Scale
- Tested up to: ~100K chunks on 16GB RAM
- ChromaDB scaling: Limited by SQLite (~1M vectors)
- Embedding batching: Required for large documents
- Query latency: ~100ms for medium collections

## 🔜 Future Enhancements
1. Streaming support for large documents
2. Batched embedding generation
3. Distributed vector storage
4. API endpoint wrapping
5. LLM integration for answer generation

## 📝 Notes
- Keep vector store outside version control
- Use batching for large document sets
- Monitor memory usage with large collections
- Consider cloud hosting for production scale

---
*Last updated: November 2, 2025*
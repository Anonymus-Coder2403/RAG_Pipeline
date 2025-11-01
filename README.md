# RAG (Retrieval Augmented Generation) Pipeline Project

A production-ready, modular RAG pipeline for answering questions from PDF documents using semantic search and Google Gemini AI.

## 📁 Project Structure
```
RAG/
├── src/                        # Modular source code
│   ├── __init__.py            # Package initialization
│   ├── data_loader.py         # PDF loading and chunking
│   ├── embedding.py           # Embedding generation
│   ├── vectorstore.py         # ChromaDB vector storage
│   ├── search.py              # Document retrieval
│   ├── llm.py                 # Gemini LLM wrapper
│   └── rag_pipeline.py        # Complete RAG orchestration
├── data/
│   ├── pdf/                   # PDF documents for processing
│   ├── text_files/            # Text files containing ML/DL content
│   └── vector_store/          # Persistent vector database
├── notebook/
│   ├── document.ipynb         # Document processing notebook
│   └── pdf_loader.ipynb       # PDF processing and embedding pipeline
├── example.py                 # Usage examples
├── .env                       # Environment variables (API keys)
├── .env.example               # Template for environment variables
├── requirements.txt           # Python dependencies
└── README.md
```

## 🚀 Overview
This project implements a complete RAG (Retrieval Augmented Generation) pipeline for processing PDF documents and answering questions using AI. The system combines semantic search with Google Gemini for accurate, source-grounded answers.

## ✨ Key Features
- **📄 PDF Processing**: Automatic loading and chunking of PDF documents
- **🔍 Semantic Search**: Vector-based similarity search using sentence transformers
- **💾 Persistent Storage**: ChromaDB for efficient vector storage and retrieval
- **🤖 AI-Powered Answers**: Google Gemini 2.5 Flash for generating accurate, grounded responses
- **🏗️ Modular Design**: Clean, maintainable code split into focused modules
- **📌 Source Citation**: Automatic tracking and citation of source documents
- **⚙️ Configurable**: Easy to customize embedding models, chunk sizes, and generation parameters

## 🎯 Architecture
```
📄 PDF Documents
    ↓
🔪 Text Chunking (RecursiveCharacterTextSplitter)
    ↓
🧠 Embeddings (all-MiniLM-L6-v2, 384 dimensions)
    ↓
💾 Vector Store (ChromaDB - Persistent)
    ↓
🔍 Semantic Search (Cosine Similarity)
    ↓
🤖 Answer Generation (Gemini 2.5 Flash)
    ↓
✨ Final Answer with Citations
```

## 📋 Requirements
```python
langchain-community
langchain-text-splitters
sentence-transformers
chromadb
numpy
scikit-learn
pypdf
google-generativeai
python-dotenv
```

## 💻 Installation

### 1. Clone and Setup
```bash
# Clone the repository
git clone https://github.com/Anonymus-Coder2403/RAG_Pipeline.git
cd RAG_Pipeline

# Create and activate virtual environment
python -m venv .venv

# Windows:
.venv\Scripts\activate

# Linux/Mac:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure API Key
```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your Gemini API key:
# GEMINI_API_KEY=your_api_key_here
```

Get your Gemini API key from: https://aistudio.google.com/app/apikey

## 🔧 Quick Start

### Option 1: Using Modular Code (Recommended)

```python
from src import (
    PDFDocumentLoader,
    EmbeddingManager,
    VectorStore,
    RAGRetriever,
    GeminiLLM,
    RAGPipeline
)

# 1. Load and process documents
loader = PDFDocumentLoader(chunk_size=1000, chunk_overlap=200)
chunks = loader.load_and_split("data/pdf")

# 2. Generate embeddings
embedding_manager = EmbeddingManager()
texts = [doc.page_content for doc in chunks]
embeddings = embedding_manager.generate_embeddings(texts)

# 3. Store in vector database
vector_store = VectorStore()
vector_store.add_documents(chunks, embeddings)

# 4. Set up RAG pipeline
retriever = RAGRetriever(vector_store, embedding_manager)
llm = GeminiLLM()
rag = RAGPipeline(retriever, llm)

# 5. Ask questions!
result = rag.answer("What are news values?", top_k=3)
rag.display_result(result)
```

### Option 2: Quick Query (Using Existing Vector Store)

If you've already processed documents:

```python
from src import EmbeddingManager, VectorStore, RAGRetriever, GeminiLLM, RAGPipeline

# Connect to existing vector store
embedding_manager = EmbeddingManager()
vector_store = VectorStore()
retriever = RAGRetriever(vector_store, embedding_manager)
llm = GeminiLLM()
rag = RAGPipeline(retriever, llm)

# Ask questions
result = rag.answer("Your question here", top_k=3)
print(result['answer'])
```

### Option 3: Run Example Script

```bash
python example.py
```

## 📚 Module Documentation

### 📄 `PDFDocumentLoader`
Handles loading and chunking PDF documents.

**Parameters:**
- `chunk_size` (int): Maximum size of text chunks (default: 1000)
- `chunk_overlap` (int): Overlap between chunks (default: 200)
- `separators` (list): Custom separators for splitting (default: ["\n\n", "\n", " ", ""])

**Methods:**
- `load_pdfs(pdf_directory)`: Load all PDFs from a directory
- `split_documents(documents)`: Split documents into chunks
- `load_and_split(pdf_directory)`: Combined load and split operation

### 🧠 `EmbeddingManager`
Generates embeddings using SentenceTransformers.

**Parameters:**
- `model_name` (str): HuggingFace model name (default: "all-MiniLM-L6-v2")

**Methods:**
- `generate_embeddings(texts, show_progress)`: Generate embeddings for text list
- `get_embedding_dimension()`: Get embedding dimension

### 💾 `VectorStore`
Manages ChromaDB vector storage.

**Parameters:**
- `collection_name` (str): Name of collection (default: "pdf_documents")
- `persist_directory` (str): Storage directory (default: "../data/vector_store")

**Methods:**
- `add_documents(documents, embeddings)`: Add documents to store
- `get_collection_stats()`: Get collection statistics
- `clear_collection()`: Delete all documents

### 🔍 `RAGRetriever`
Handles semantic search and document retrieval.

**Parameters:**
- `vector_store`: VectorStore instance
- `embedding_manager`: EmbeddingManager instance

**Methods:**
- `retrieve(query, top_k, score_threshold)`: Retrieve relevant documents

### 🤖 `GeminiLLM`
Wrapper for Google Gemini API.

**Parameters:**
- `model_name` (str): Gemini model (default: "gemini-2.5-flash")
- `temperature` (float): Sampling temperature (default: 0.1)
- `max_output_tokens` (int): Max response length (default: 500)
- `top_p` (float): Nucleus sampling (default: 0.95)
- `top_k` (int): Top-k sampling (default: 40)
- `api_key` (str): Google AI API key (optional)

**Methods:**
- `generate(prompt, max_retries)`: Generate response with retry logic
- `list_available_models()`: List available Gemini models

### 🔗 `RAGPipeline`
Complete RAG pipeline orchestrator.

**Parameters:**
- `retriever`: RAGRetriever instance
- `llm`: GeminiLLM instance

**Methods:**
- `answer(query, top_k)`: Complete RAG pipeline (retrieve + generate)
- `display_result(result)`: Format and display result

## ⚙️ Configuration

### Embedding Models
Choose different embedding models from HuggingFace:

- **`all-MiniLM-L6-v2`** (default): Fast, general-purpose (384 dim)
- **`BAAI/bge-large-en-v1.5`**: High quality for technical content (1024 dim)
- **`sentence-transformers/all-mpnet-base-v2`**: Balanced quality/speed (768 dim)

### Gemini Models
Available models (check with `GeminiLLM.list_available_models()`):

- **`gemini-2.5-flash`** (default): Fast, cost-effective
- **`gemini-2.5-pro`**: Higher quality, slower
- **`gemini-2.0-flash`**: Alternative fast model

### RAG Parameters

**Chunking:**
- `chunk_size`: 1000 characters (balance between context and specificity)
- `chunk_overlap`: 200 characters (maintains context across chunks)

**Retrieval:**
- `top_k`: 3-5 chunks (more = more context but higher cost)
- `score_threshold`: 0.0-1.0 (filter low-similarity results)

**Generation:**
- `temperature`: 0.1 (low for factual responses)
- `max_output_tokens`: 500 (adjust based on needs)

## 🚨 Troubleshooting

### API Key Issues
```
Error: GEMINI_API_KEY not found
Solution: Create .env file with GEMINI_API_KEY=your_key_here
```

### Model Not Found
```
Error: 404 models/gemini-xxx not found
Solution: Run GeminiLLM.list_available_models() to see available models
```

### Low Similarity Scores
```
Issue: Retrieval returns low similarity scores
Solutions:
- Check if embedding model matches document type
- Try different embedding model (e.g., BAAI/bge-large-en-v1.5)
- Adjust chunk_size and chunk_overlap
- Add more relevant documents
```

## 💡 Performance Tips

1. **Vector Store Persistence**: ChromaDB automatically persists data - no need to re-process documents each run
2. **Batch Processing**: Process multiple PDFs at once for efficiency
3. **Embedding Model Selection**:
   - Use `all-MiniLM-L6-v2` for general documents
   - Use `BAAI/bge-large-en-v1.5` for technical/academic content
4. **Chunk Size Optimization**:
   - Smaller chunks (500-800): More precise retrieval
   - Larger chunks (1000-1500): More context per chunk

## 🔍 Core Notebook: `pdf_loader.ipynb`

The [`notebook/pdf_loader.ipynb`](notebook/pdf_loader.ipynb) contains the development process showing:
- PDF loading and text extraction
- Text chunking with RecursiveCharacterTextSplitter
- Embedding generation using sentence-transformers
- ChromaDB vector storage setup
- Gemini LLM integration
- Complete RAG pipeline implementation

This forms the foundation of the entire RAG system, demonstrating how document parsing, vector storage, and LLM context retrieval work together.

## 🤝 Contributing
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Authors
- Yash Kumar (@Anonymus-Coder2403)

## 🙏 Acknowledgments

This project uses the following amazing technologies:

- **[LangChain](https://www.langchain.com/)**: Document loading and processing
- **[Sentence Transformers](https://www.sbert.net/)**: State-of-the-art embedding generation
- **[ChromaDB](https://www.trychroma.com/)**: Efficient vector database
- **[Google Gemini](https://ai.google.dev/)**: AI-powered answer generation

## 📖 Additional Resources

- [Original Notebook](notebook/pdf_loader.ipynb): Development notebook with step-by-step process
- [Example Script](example.py): Ready-to-run usage examples
- [API Documentation](https://ai.google.dev/docs): Google Gemini API docs

---

⭐ **Star this repo if you found it helpful!**

**Built with ❤️ for the open-source community**

# Traditional RAG (Retrieval Augmented Generation) Pipeline 

## 📁 Project Structure
```
RAG/
├── data/
│   ├── pdf/            # PDF documents for processing
│   └── text_files/     # Text files containing ML/DL content
├── notebook/
│   ├── document.ipynb  # Document processing notebook
│   └── pdf_loader.ipynb # PDF processing and embedding pipeline
└── README.md
```

## 🚀 Overview
This project implements a RAG (Retrieval Augmented Generation) pipeline for processing and analyzing documents. It includes capabilities for handling both PDF and text files, with support for document chunking and embedding generation.

## 🛠️ Features
- **Document Processing**
  - PDF document loading and parsing
  - Text file processing
  - Metadata extraction and management
- **Text Processing**
  - Recursive character-based text splitting
  - Configurable chunk sizes and overlap
  - Custom separator support
- **Embedding Generation**
  - Sentence transformer integration (`all-MiniLM-L6-v2`)
  - Vector database storage (ChromaDB)
  - Cosine similarity search

## 📋 Requirements
```python
langchain-community
langchain-text-splitters
sentence-transformers
chromadb
numpy
sklearn
pypdf
```

## 💻 Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/RAG.git
cd RAG

# Create and activate virtual environment (Windows)
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## 🔧 Usage
### 1. Document Processing
```python
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader

# Process PDF documents
pdf_documents = process_all_pdfs("path/to/pdf/directory")
```

### 2. Text Splitting
```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Split documents into chunks
chunks = split_documents(documents, chunk_size=1000, chunk_overlap=200)
```

### 3. Embedding Generation
```python
from sentence_transformers import SentenceTransformer

# Initialize embedding manager
embedding_manager = EmbeddingManager(model_name="all-MiniLM-L6-v2")
```

## 📊 Project Components
1. **Document Loader (`document.ipynb`)**
   - Handles text file ingestion
   - Document structure management
   - Basic text processing

2. **PDF Pipeline (`notebook/pdf_loader.ipynb`)**
   - PDF document processing
   - Text chunking
   - Embedding generation
   - Vector database integration

## 🔍 Code Examples
### PDF Processing
```python
def process_all_pdfs(pdf_directory):
    """Process all PDF files in a directory"""
    all_documents = []
    pdf_dir = Path(pdf_directory)
    # ... processing logic
    return all_documents
```

### Text Splitting
```python
def split_documents(documents, chunk_size=1000, chunk_overlap=200):
    """Split documents into smaller chunks"""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    # ... splitting logic
    return split_docs
```

## 📝 Notes
- Ensure PDF files are placed in the `data/pdf` directory
- Text files should be placed in `data/text_files`
- Default model: `all-MiniLM-L6-v2`
- Default chunk size: 1000 characters
- Default chunk overlap: 200 characters

## 🤝 Contributing
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Authors
- Yash Kumar (@yourusername)

## 🙏 Acknowledgments
- LangChain Community
- Sentence Transformers
- ChromaDB Team

---
*For more information, please refer to the individual notebook documentation.*

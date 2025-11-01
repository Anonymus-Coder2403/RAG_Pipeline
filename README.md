# Traditional RAG (Retrieval-Augmented Generation) Pipeline

This repository implements a **Retrieval-Augmented Generation (RAG)** pipeline for processing and analyzing both PDF and text documents.  
The project demonstrates document ingestion, text chunking, embedding generation, and vector database storage for efficient semantic retrieval.

The **core of the project** lies in the [`notebook/pdf_loader.ipynb`](notebook/pdf_loader.ipynb), where PDFs are parsed, chunked, and transformed into vector embeddings used in retrieval tasks.

---

## 📁 Project Structure

```
RAG/
├── data/
│ ├── pdf/ # PDF documents for processing
│ ├── text_files/ # Text files containing ML/DL content
│ └── vector_store/ # Chroma/FAISS vector storage (ignored in Git)
├── notebook/
│ ├── document.ipynb # Text document processing pipeline
│ └── pdf_loader.ipynb # Core PDF processing and embedding pipeline
├── main.py # script for RAG pipeline
├── requirements.txt # Python dependencies
├── pyproject.toml # Build configuration
├── README.md # Project documentation
└── .gitignore, .gitattributes, etc.
```


---

## Overview

This project is built to demonstrate **how retrieval-based systems enhance LLMs** by augmenting generation with external document knowledge.

The pipeline:
1. **Loads and parses PDFs or text files**
2. **Chunks long content** into semantically meaningful sections
3. **Generates embeddings** using a transformer model
4. **Stores them in a vector database** (ChromaDB)
5. **Retrieves** relevant document chunks during queries

---

## Core Notebook: `pdf_loader.ipynb`

### 🔍 What It Does
| Step | Description |
|------|--------------|
| **1️⃣ Load PDFs** | Iterates through all `.pdf` files in `data/pdf/` and extracts clean text. |
| **2️⃣ Clean & Preprocess** | Removes headers, footers, and formatting artifacts. |
| **3️⃣ Chunk Text** | Splits text into overlapping chunks (default: 1000 characters, 200 overlap) using `RecursiveCharacterTextSplitter`. |
| **4️⃣ Generate Embeddings** | Uses `sentence-transformers` (`all-MiniLM-L6-v2`) to convert text chunks into numerical vectors. |
| **5️⃣ Store in ChromaDB** | Embeddings are saved into a local Chroma vector store (`data/vector_store/chroma.sqlite3`). |
| **6️⃣ Query Examples** | Demonstrates how to perform semantic search queries on stored vectors. |

### 💡 Why This Notebook Matters
- It forms the **data foundation** of the entire RAG system.  
- All retrieval, query-answering, and augmentation depend on the processed embeddings here.  
- Shows how to connect **document parsing → vector storage → LLM context retrieval** in a single pipeline.

---

## Features

### 🧾 Document Processing
- PDF and plain text file ingestion  
- Metadata extraction and management  
- Support for multiple document types  

### Text Processing
- Recursive character-based text splitting  
- Customizable chunk size and overlap  
- Configurable separators for flexible splitting  

### Embedding Generation
- Integrated with `sentence-transformers` (`all-MiniLM-L6-v2`)  
- Stores embeddings in **ChromaDB** (local vector database)  
- Supports cosine similarity search  

---

## 📋 Requirements

```txt
langchain-community
langchain-text-splitters
sentence-transformers
chromadb
numpy
scikit-learn
pypdf
```

## 💻 Installation
```bash
# Clone the repository
git clone https://github.com/Anonymus-Coder2403/RAG_Pipeline.git
cd RAG_Pipeline

# Create and activate virtual environment (Windows)
python -m venv venv
.\venv\Scripts\activate
# or (Linux/macOS)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## 🔧 Usage
### 1. Document Processing
```python
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader

# Process all PDF documents
pdf_documents = process_all_pdfs("data/pdf/")
```

### 2. Text Splitting
```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Split documents into manageable chunks
chunks = split_documents(documents, chunk_size=1000, chunk_overlap=200)
```

### 3. Embedding Generation
```python
from sentence_transformers import SentenceTransformer

# Initialize embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = model.encode(["sample text chunk"])
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
    for pdf_file in pdf_dir.glob("*.pdf"):
        loader = PyPDFLoader(str(pdf_file))
        docs = loader.load()
        all_documents.extend(docs)
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
    split_docs = text_splitter.split_documents(documents)
    return split_docs

```
## Example Query (after embedding)
```python
from chromadb import Client

client = Client()
collection = client.get_or_create_collection("pdf_embeddings")

query = "What is the key idea of the paper?"
results = collection.query(query_texts=[query], n_results=3)
print(results)

```

## Technologies Used

   - Python 3.10+
   - LangChain (document loaders, text splitting)
   - Sentence Transformers (all-MiniLM-L6-v2 embeddings)
   - ChromaDB (vector database)
   - NumPy & scikit-learn (utility math)
   - PyPDF / PDFMiner (PDF parsing)


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


## Reviewer’s Guide
- If you are reviewing this repository:

- Start with: notebook/pdf_loader.ipynb — this contains the main pipeline logic.

- Then see: notebook/document.ipynb — shows plain text handling.

- Finally: main.py — orchestrates RAG pipeline end-to-end.

- Tip: If GitHub fails to render the notebook, open it locally in Jupyter or VS Code.

```bash
jupyter notebook notebook/pdf_loader.ipynb
```
x
## 📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Authors
- Yash Kumar (@yourusername)

## Future Enhancements

- Migrate vector storage to AWS S3 + Pinecone or Weaviate Cloud
- Integrate LLM querying layer for contextual answers

---
*For more information, please refer to the individual notebook documentation.*

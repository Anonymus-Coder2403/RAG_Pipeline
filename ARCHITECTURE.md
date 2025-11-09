# System Architecture Documentation

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER BROWSER                            │
│                    http://localhost:8501                        │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    STREAMLIT APPLICATION                        │
│                         (app.py)                                │
│                                                                 │
│  ┌──────────────────┐                    ┌──────────────────┐  │
│  │   File Upload    │                    │   Chat Interface │  │
│  │   Widget         │                    │   (Messages)     │  │
│  └────────┬─────────┘                    └────────┬─────────┘  │
│           │                                        │            │
│           │         Session State (st.session_state)           │
│           │         - session_id                   │            │
│           │         - messages[]                   │            │
│           │         - uploaded_files_info[]        │            │
│           │                                        │            │
└───────────┼────────────────────────────────────────┼────────────┘
            │                                        │
            ▼                                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                     SERVICES LAYER                              │
│                                                                 │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐ │
│  │ DocumentService  │  │   RAGService     │  │SessionService│ │
│  │                  │  │                  │  │              │ │
│  │ • validate_file  │  │ • process_doc    │  │• create()    │ │
│  │ • save_file      │  │ • query()        │  │• get_session │ │
│  │ • sanitize_name  │  │ • health_check() │  │• update()    │ │
│  │ • cleanup()      │  │ • get_stats()    │  │• delete()    │ │
│  └────────┬─────────┘  └────────┬─────────┘  └──────┬───────┘ │
│           │                     │                    │         │
└───────────┼─────────────────────┼────────────────────┼─────────┘
            │                     │                    │
            ▼                     ▼                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                    CORE RAG MODULES (src/)                      │
│                                                                 │
│  ┌────────────────┐  ┌────────────────┐  ┌─────────────────┐  │
│  │PDFDocumentLoader│  │EmbeddingManager│  │  VectorStore    │  │
│  │                │  │                │  │   (ChromaDB)    │  │
│  │• load_pdf()    │  │• generate()    │  │• add_documents()│  │
│  │• split_text()  │  │• get_dim()     │  │• query()        │  │
│  └───────┬────────┘  └───────┬────────┘  └────────┬────────┘  │
│          │                   │                     │           │
│          │                   │                     │           │
│  ┌───────┴───────────────────┴─────────────────────┴────────┐  │
│  │                    RAGPipeline                           │  │
│  │  • retrieve_context()                                    │  │
│  │  • generate_answer()                                     │  │
│  │  • format_response()                                     │  │
│  └───────┬──────────────────────────────────────────────────┘  │
│          │                                                     │
│  ┌───────┴─────────┐                                           │
│  │   GeminiLLM     │                                           │
│  │ • generate()    │                                           │
│  └───────┬─────────┘                                           │
└──────────┼─────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    EXTERNAL SERVICES                            │
│                                                                 │
│  ┌──────────────────┐              ┌──────────────────┐        │
│  │  Gemini API      │              │  SentenceTransf. │        │
│  │  (Google AI)     │              │  (HuggingFace)   │        │
│  └──────────────────┘              └──────────────────┘        │
└─────────────────────────────────────────────────────────────────┘

           ▼                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PERSISTENT STORAGE                           │
│                                                                 │
│  ┌──────────────────┐              ┌──────────────────┐        │
│  │  data/uploads/   │              │data/vector_store/│        │
│  │  (Temp Files)    │              │  (ChromaDB)      │        │
│  └──────────────────┘              └──────────────────┘        │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow: Document Upload

```
User Uploads PDF
      │
      ▼
┌─────────────────────────────────────┐
│ 1. File Upload (Streamlit Widget)  │
└──────────────┬──────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────────────┐
│ 2. DocumentService.save_uploaded_file()                  │
│    • Validate file type (.pdf, .txt, .docx)              │
│    • Check file size (< MAX_FILE_SIZE_MB)                │
│    • Sanitize filename (prevent path traversal)          │
│    • Save to data/uploads/{session_id}/{filename}        │
└──────────────┬───────────────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────────────┐
│ 3. RAGService.process_document()                         │
│    ┌──────────────────────────────────────────────┐     │
│    │ 3a. PDFDocumentLoader.load_and_split()       │     │
│    │     • Parse PDF with PyPDF                   │     │
│    │     • Extract text + metadata                │     │
│    │     • Split into chunks (size=1000, overlap=200) │  │
│    └──────────────────────────────────────────────┘     │
│                                                          │
│    ┌──────────────────────────────────────────────┐     │
│    │ 3b. EmbeddingManager.generate_embeddings()   │     │
│    │     • Use SentenceTransformer (all-MiniLM)   │     │
│    │     • Convert text → 384-dim vectors         │     │
│    │     • Batch processing for efficiency        │     │
│    └──────────────────────────────────────────────┘     │
│                                                          │
│    ┌──────────────────────────────────────────────┐     │
│    │ 3c. VectorStore.add_documents()              │     │
│    │     • Store vectors in ChromaDB              │     │
│    │     • Persist to data/vector_store/          │     │
│    │     • Create collection if needed            │     │
│    └──────────────────────────────────────────────┘     │
└──────────────┬───────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ 4. Update Session State             │
│    • Add file to uploaded_files     │
│    • Update document count          │
│    • Display success message        │
└─────────────────────────────────────┘
```

## Data Flow: User Query

```
User Types Question
      │
      ▼
┌─────────────────────────────────────┐
│ 1. Chat Input (Streamlit)          │
└──────────────┬──────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────────────┐
│ 2. RAGService.query(question, collection_name, top_k)    │
│    ┌──────────────────────────────────────────────┐     │
│    │ 2a. EmbeddingManager.generate_embeddings()   │     │
│    │     • Convert question → 384-dim vector      │     │
│    └──────────────────────────────────────────────┘     │
│                                                          │
│    ┌──────────────────────────────────────────────┐     │
│    │ 2b. VectorStore.query()                      │     │
│    │     • Semantic search in ChromaDB            │     │
│    │     • Cosine similarity ranking              │     │
│    │     • Return top-k chunks (default k=3)      │     │
│    └──────────────────────────────────────────────┘     │
│                                                          │
│    ┌──────────────────────────────────────────────┐     │
│    │ 2c. RAGPipeline.build_context()              │     │
│    │     • Concatenate retrieved chunks           │     │
│    │     • Add source metadata (file, page)       │     │
│    └──────────────────────────────────────────────┘     │
│                                                          │
│    ┌──────────────────────────────────────────────┐     │
│    │ 2d. GeminiLLM.generate_response()            │     │
│    │     • Build prompt with context              │     │
│    │     • Call Gemini API                        │     │
│    │     • Parse response                         │     │
│    └──────────────────────────────────────────────┘     │
│                                                          │
│    ┌──────────────────────────────────────────────┐     │
│    │ 2e. Format Result                            │     │
│    │     • Answer text                            │     │
│    │     • Source citations                       │     │
│    │     • Similarity scores                      │     │
│    └──────────────────────────────────────────────┘     │
└──────────────┬───────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ 3. Display Result                   │
│    • Show answer in chat            │
│    • Show sources in expander       │
│    • Add to message history         │
└─────────────────────────────────────┘
```

## Session Management Flow

```
User Visits App
      │
      ▼
┌─────────────────────────────────────┐
│ Check if session_id exists?         │
└──────────┬──────────────────────────┘
           │
    ┌──────┴──────┐
    │ No          │ Yes
    ▼             ▼
┌───────────┐  ┌──────────────────────┐
│ Create    │  │ Load Existing Session│
│ New       │  │ • Get session data   │
│ Session   │  │ • Update last_activity│
│ ID (UUID) │  │ • Load messages      │
└───────────┘  └──────────────────────┘
    │                   │
    └─────────┬─────────┘
              ▼
┌─────────────────────────────────────┐
│ Session Active                      │
│ • session_id: abc123                │
│ • collection: session_abc123        │
│ • messages: []                      │
│ • uploaded_files_info: []           │
└──────────────┬──────────────────────┘
               │
         ┌─────┴─────┐
         │           │
    Upload File   Ask Question
         │           │
         ▼           ▼
    Update Session State
         │
         ▼
┌─────────────────────────────────────┐
│ User Clicks "Clear Session"?        │
└──────────┬──────────────────────────┘
           │
           ▼ Yes
┌─────────────────────────────────────┐
│ Cleanup Session                     │
│ • Delete ChromaDB collection        │
│ • Delete uploaded files             │
│ • Clear message history             │
│ • Create new session                │
└─────────────────────────────────────┘
```

## Component Responsibilities

### Presentation Layer (app.py)
**Responsibility:** User interface and interaction
- Render UI components (file upload, chat)
- Manage Streamlit session state
- Display messages and sources
- Handle user input events
- Show progress indicators and errors

**Dependencies:**
- services.DocumentService
- services.RAGService
- services.SessionService
- config

---

### Business Logic Layer (services/)

#### DocumentService
**Responsibility:** File management
- Validate uploaded files (type, size, content)
- Sanitize filenames (security)
- Save files to temporary storage
- Cleanup session files
- Extract file metadata

**Dependencies:**
- config
- pathlib, hashlib, shutil

#### RAGService
**Responsibility:** RAG orchestration
- Process documents (load → chunk → embed → store)
- Execute queries (embed → retrieve → generate)
- Manage ChromaDB collections
- Health checks
- Error handling and logging

**Dependencies:**
- src.PDFDocumentLoader
- src.EmbeddingManager
- src.VectorStore
- src.RAGRetriever
- src.GeminiLLM
- src.RAGPipeline
- config

#### SessionService
**Responsibility:** Session lifecycle
- Create unique session IDs
- Track session metadata (documents, queries)
- Manage session expiry
- Cleanup expired sessions
- Provide session statistics

**Dependencies:**
- uuid, datetime
- config

---

### Data Access Layer (src/)

#### PDFDocumentLoader
**Responsibility:** Document loading and chunking
- Parse PDF files (PyPDF)
- Extract text and metadata
- Split into chunks (RecursiveCharacterTextSplitter)
- Handle errors (corrupt PDFs, etc.)

#### EmbeddingManager
**Responsibility:** Vector embeddings
- Load SentenceTransformer model
- Generate embeddings (text → vectors)
- Batch processing
- Model caching

#### VectorStore
**Responsibility:** Vector database operations
- Connect to ChromaDB
- Create/manage collections
- Add documents with embeddings
- Query for similar vectors
- Persist to disk

#### RAGRetriever
**Responsibility:** Document retrieval
- Query vector store
- Rank by similarity
- Return top-k results
- Format results with metadata

#### GeminiLLM
**Responsibility:** Answer generation
- Connect to Gemini API
- Build prompts
- Generate responses
- Retry logic for failures
- Token management

#### RAGPipeline
**Responsibility:** End-to-end RAG flow
- Orchestrate retrieval + generation
- Build context from chunks
- Format final response
- Add source citations

---

## Security Architecture

### Input Validation
```
User Input
    │
    ▼
┌─────────────────────────────────────┐
│ File Validation                     │
│ • Extension check (.pdf, .txt, etc.)│
│ • Size limit (< 10MB)               │
│ • Content validation (not empty)    │
│ • Filename sanitization             │
│   - Remove path traversal (..)      │
│   - Remove special chars (<>|"*?)   │
│   - Limit length (100 chars)        │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│ Query Validation                    │
│ • Not empty                         │
│ • Length limit (configurable)       │
│ • No injection attempts             │
└─────────────────────────────────────┘
```

### Secret Management
```
┌─────────────────────────────────────┐
│ .env File (gitignored)              │
│ GEMINI_API_KEY=secret_key           │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ config.py                           │
│ api_key = os.getenv("GEMINI_API_KEY")│
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ Services (use config.GEMINI_API_KEY)│
│ • Never logged                      │
│ • Never shown to users              │
│ • Never committed to git            │
└─────────────────────────────────────┘
```

### Session Isolation
```
User A                    User B
  │                         │
  ▼                         ▼
session_a123            session_b456
  │                         │
  ▼                         ▼
collection_a123         collection_b456
  │                         │
  ▼                         ▼
User A's docs           User B's docs
(isolated)              (isolated)
```

---

## Error Handling Architecture

### Layered Error Handling
```
┌─────────────────────────────────────┐
│ UI Layer (app.py)                   │
│ • Catch service errors              │
│ • Display user-friendly messages    │
│ • Show error in st.error()          │
│ • Continue execution (no crash)     │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ Service Layer (services/)           │
│ • Try-catch all operations          │
│ • Log errors with stack traces      │
│ • Return (data, error) tuples       │
│ • Never raise exceptions to UI      │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ Data Layer (src/)                   │
│ • Validate inputs                   │
│ • Retry transient failures (API)    │
│ • Raise exceptions with context     │
│ • Log low-level errors              │
└─────────────────────────────────────┘
```

### Example Error Flow
```
User uploads corrupt PDF
    │
    ▼
PDFDocumentLoader.load_pdf()
    │ PyPDF raises exception
    ▼
RAGService.process_document()
    │ Catches exception
    │ Logs: "Error processing document: {error}"
    │ Returns: (None, "Failed to parse PDF")
    ▼
app.py
    │ Checks error != None
    │ Displays: st.error("Processing failed: ...")
    ▼
User sees friendly error
Session continues (no crash)
```

---

## Scalability Considerations

### Current Architecture (MVP)
```
┌────────────┐
│ Streamlit  │
│ Instance   │
└──────┬─────┘
       │
       ▼
┌────────────┐     ┌──────────────┐
│ ChromaDB   │     │ Gemini API   │
│ (SQLite)   │     │ (External)   │
└────────────┘     └──────────────┘

Limits:
• Single instance (no load balancing)
• SQLite (single-threaded, ~1M vectors max)
• Session data in memory
• File storage on local disk
```

### Scaled Architecture (Future)
```
┌────────────┐   ┌────────────┐   ┌────────────┐
│ Streamlit  │   │ Streamlit  │   │ Streamlit  │
│ Instance 1 │   │ Instance 2 │   │ Instance 3 │
└──────┬─────┘   └──────┬─────┘   └──────┬─────┘
       │                │                │
       └────────────────┼────────────────┘
                        │
          ┌─────────────┴─────────────┐
          │                           │
          ▼                           ▼
    ┌──────────┐              ┌──────────────┐
    │  Redis   │              │ Pinecone     │
    │ (Session)│              │ (Vectors)    │
    └──────────┘              └──────────────┘
                                     │
                                     ▼
                              ┌──────────────┐
                              │  S3/GCS      │
                              │  (Files)     │
                              └──────────────┘

Benefits:
• Horizontal scaling (multiple instances)
• Shared session state (Redis)
• Cloud vector DB (millions of vectors)
• Shared file storage (S3/GCS)
• Load balancing
```

---

## Deployment Architecture

### Docker Deployment
```
┌─────────────────────────────────────────────┐
│           Docker Container                  │
│  ┌───────────────────────────────────────┐  │
│  │  Streamlit App (port 8501)            │  │
│  └───────────────────────────────────────┘  │
│                                             │
│  Mounted Volumes:                           │
│  • data/vector_store → /app/data/vector    │
│  • data/uploads → /app/data/uploads        │
│                                             │
│  Environment:                               │
│  • GEMINI_API_KEY (from .env)              │
│  • ENVIRONMENT=production                   │
└─────────────────────────────────────────────┘
```

### Cloud Deployment (AWS Example)
```
Internet
   │
   ▼
┌────────────────┐
│ Application    │
│ Load Balancer  │
│ (HTTPS)        │
└───────┬────────┘
        │
   ┌────┴────┐
   │         │
   ▼         ▼
┌─────┐   ┌─────┐
│ ECS │   │ ECS │  (Fargate containers)
│Task1│   │Task2│
└──┬──┘   └──┬──┘
   │         │
   └────┬────┘
        │
   ┌────┴─────────────┐
   │                  │
   ▼                  ▼
┌─────┐          ┌──────────┐
│ EFS │          │ Secrets  │
│Store│          │ Manager  │
└─────┘          └──────────┘
(vector_store)   (API keys)
```

---

## Monitoring Architecture

### Logging Flow
```
Application Events
   │
   ▼
Python logging module
   │
   ├─ INFO:  Normal operations
   ├─ WARNING: Recoverable issues
   ├─ ERROR: Failed operations
   └─ DEBUG: Detailed debugging
   │
   ▼
stdout/stderr
   │
   ▼
Docker logs
   │
   ▼
Log aggregation
(CloudWatch/Datadog/etc.)
   │
   ▼
Alerts & Dashboards
```

### Metrics to Track (Future)
```
┌────────────────────────────────────┐
│ Application Metrics                │
├────────────────────────────────────┤
│ • Requests per second              │
│ • Response time (p50, p95, p99)    │
│ • Error rate                       │
│ • Document processing time         │
│ • Query latency                    │
│ • Active sessions                  │
└────────────────────────────────────┘

┌────────────────────────────────────┐
│ Business Metrics                   │
├────────────────────────────────────┤
│ • Documents uploaded per day       │
│ • Queries per day                  │
│ • Active users                     │
│ • Gemini API cost (tokens)         │
│ • Average session duration         │
└────────────────────────────────────┘
```

---

## Technology Stack

### Frontend
- **Streamlit** (1.31+): Web UI framework
- **Python** (3.11): Programming language

### Backend Services
- **Custom Services Layer**: Business logic
- **LangChain**: RAG framework components
- **SentenceTransformers**: Embedding generation
- **ChromaDB**: Vector database

### External APIs
- **Google Gemini 2.5 Flash**: LLM for generation
- **HuggingFace**: Model hosting (embeddings)

### Deployment
- **Docker**: Containerization
- **Docker Compose**: Orchestration
- **Streamlit Cloud / Railway / AWS**: Hosting

### Dependencies
```
langchain>=0.1.0              # RAG framework
langchain-core>=0.1.0         # Core abstractions
langchain-community>=0.0.20   # Community integrations
pypdf>=3.17.0                 # PDF parsing
sentence-transformers>=2.2.0  # Embeddings
chromadb>=0.4.22              # Vector DB
google-generativeai>=0.3.0    # Gemini API
streamlit>=1.31.0             # Web UI
python-dotenv>=1.0.0          # Environment variables
```

---

## Performance Characteristics

### Latency Breakdown (Typical Query)
```
Total: ~3-5 seconds
├─ Embedding generation: 0.5-1s
├─ Vector search: 0.2-0.5s
├─ LLM generation: 2-3s
└─ Overhead: 0.3-0.5s
```

### Throughput
- **Single instance:** ~10-20 queries/minute
- **With caching:** ~100+ queries/minute (repeat queries)
- **Scaled (3 instances):** ~30-60 queries/minute

### Resource Usage
- **Memory:** ~1-2GB (depending on model size)
- **CPU:** 1-2 cores (sufficient for most workloads)
- **Storage:** ~100MB base + documents + vector store

---

## Configuration Matrix

| Setting | Development | Production |
|---------|-------------|------------|
| LOG_LEVEL | DEBUG | WARNING |
| ENVIRONMENT | development | production |
| ENABLE_CACHING | true | true |
| SESSION_COLLECTIONS | true | true |
| MAX_FILE_SIZE_MB | 10 | 10 |
| TOP_K_RESULTS | 3 | 3 |
| CHUNK_SIZE | 1000 | 1000 |
| LLM_TEMPERATURE | 0.1 | 0.1 |

---

**This architecture supports:**
- ✅ 100+ concurrent users (with scaling)
- ✅ Millions of documents (with cloud vector DB)
- ✅ Sub-5-second query latency
- ✅ 99.9% uptime (with proper deployment)
- ✅ Horizontal scaling (stateless design)
- ✅ Multi-tenant isolation (session collections)

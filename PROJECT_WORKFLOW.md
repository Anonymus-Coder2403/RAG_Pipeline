# RAG Upgraded — End-to-End Project Workflow (PPT-Ready)

This guide captures the full Retrieval-Augmented Generation (RAG) workflow in this repo, with a step-by-step “voodoo” diagram, exact prompts to generate a presentation and diagrams with AI tools, and a short executive summary. You can paste the prompts into ChatGPT (or your preferred tool) to auto-generate PPT content and visuals.

---

## 1) Executive Summary (Short)

- Goal: Answer user questions grounded in uploaded documents using a production-grade RAG stack (Streamlit UI, SentenceTransformers, ChromaDB, Gemini LLM).
- Flow: Upload → Extract & Chunk → Embed → Persist → Retrieve → Prompt LLM → Answer + Sources.
- Highlights: Modular code, session-scoped collections, persistent vector store, health checks, Dockerized deployment.

---

## 2) High-Level Workflow (Step-by-Step)

1. User opens Streamlit app (`app.py`) and starts a session.
2. User uploads documents (PDF/TXT/DOCX). DocumentService validates, sanitizes, and stores files per-session.
3. RAGService processes the file: extract text pages → split into chunks (size/overlap from config).
4. EmbeddingManager encodes chunks into vectors (SentenceTransformers; GPU if available).
5. VectorStore persists vectors + metadata in ChromaDB (per-session collection optional).
6. User types a query in chat. QueryClassifier routes to RAG (if doc-search intent) or direct LLM chat.
7. For RAG: Embed query → ChromaDB similarity search → top-k chunks returned.
8. RAGPipeline builds a grounded prompt with retrieved context → Gemini LLM generates an answer.
9. UI displays answer and expandable source citations with similarity scores.
10. SessionService tracks stats (documents, queries). Users can clear session and collections.

---

## 3) Detailed “Voodoo” Workflow Diagram (ASCII)

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                            0) CONFIG & ENV                                   │
│  .env → GEMINI_API_KEY • config.py → CHUNK_SIZE, TOP_K, MODEL, DIRS          │
└──────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                            1) WEB UI (Streamlit)                              │
│  app.py: cache services • init session • sidebar upload • chat input         │
└──────────────────────────────────────────────────────────────────────────────┘
                                     │
                  Upload File (PDF/TXT/DOCX) or Ask a Question                 │
                                     ▼
┌──────────────────────────────────────┐      ┌────────────────────────────────┐
│ 2) DocumentService (services/)       │      │ 6) QueryClassifier (src/)      │
│ - validate_file (size/ext/safety)    │      │ - detect RAG triggers          │
│ - sanitize_filename                  │      │ - route: RAG or LLM            │
│ - save_uploaded_file (per session)   │      └────────────────────────────────┘
└──────────────────────────────────────┘                     │
                                     ▼                      │
┌──────────────────────────────────────┐                     │
│ 3) RAGService.process_document       │                     │
│ - extract pages (PyPDFLoader)        │                     │
│ - split chunks (Recursive splitter)  │                     │
│ - embed with EmbeddingManager        │                     │
│ - persist to VectorStore (ChromaDB)  │                     │
└──────────────────────────────────────┘                     │
                                     │                      │
                                     ▼                      ▼
┌──────────────────────────────────────┐      ┌────────────────────────────────┐
│ 4) EmbeddingManager (src/)           │      │ 7) RAG Query Path              │
│ - SentenceTransformer load (CPU/GPU) │      │ - embed query                  │
│ - encode chunks → vectors            │      │ - VectorStore.collection.query │
└──────────────────────────────────────┘      │ - top-k docs + metadata        │
                                     │        └────────────────────────────────┘
                                     ▼                      │
┌──────────────────────────────────────┐                     │
│ 5) VectorStore (src/)                │                     │
│ - PersistentClient(path=data/vec)    │                     │
│ - add(ids, embeddings, metadatas)    │                     │
│ - stats / clear_collection           │                     │
└──────────────────────────────────────┘                     │
                                                            ▼
                                           ┌──────────────────────────────────┐
                                           │ 8) RAGPipeline (src/)            │
                                           │ - build prompt with context      │
                                           │ - GeminiLLM.generate             │
                                           └──────────────────────────────────┘
                                                            │
                                                            ▼
                                           ┌──────────────────────────────────┐
                                           │ 9) UI Render                     │
                                           │ - assistant answer               │
                                           │ - sources (file, page, score)    │
                                           └──────────────────────────────────┘
```

Legend: Services = orchestration; src/* = core modules; data/* = persisted state.

---

## 4) Mermaid Diagram (for docs/diagrams-as-code)

```mermaid
flowchart TD
  A[Start App + Load Config] --> B[Create Session]
  B --> C{User Action}
  C -->|Upload Document| D[DocumentService: Validate + Save]
  D --> E[RAGService.process_document]
  E --> E1[Extract Pages]
  E1 --> E2[Chunk Text]
  E2 --> E3[EmbeddingManager.encode]
  E3 --> E4[VectorStore.add (ChromaDB)]
  C -->|Ask Question| F[QueryClassifier: RAG or LLM]
  F -->|RAG| G[Embed Query]
  G --> H[VectorStore.query Top-K]
  H --> I[RAGPipeline: Build Prompt + Gemini]
  F -->|LLM| I
  I --> J[Answer + Sources to UI]
```

---

## 5) Prompts To Auto‑Generate a PPT and Diagrams (Paste into ChatGPT)

Use the following crafted prompt in ChatGPT (GPT‑4o or equivalent). Replace bracketed items as needed.

Prompt 1 — Generate a full PPT deck outline + slide content:

"""
System
You are a senior AI Technical Writer and Solutions Architect. Produce an accurate, clear, presentation‑ready deck for an engineering and product audience. Prefer grounded, specific explanations tied to the provided code structure.

User
Context: I’m building a production RAG chatbot that uses Streamlit for UI, SentenceTransformers for embeddings, ChromaDB for vector storage, and Google Gemini as the LLM. The repository modules are:
- UI: app.py (Streamlit)
- Services: services/document_service.py, services/rag_service.py, services/session_service.py
- Core RAG: src/data_loader.py, src/embedding.py, src/vectorstore.py, src/search.py, src/llm.py, src/rag_pipeline.py
- Config: config.py
- Data dirs: data/uploads, data/vector_store, data/pdf

Task: Create a complete PowerPoint slide deck (slide titles + detailed bullet content) covering:
1) Executive Summary (what, why, outcomes)
2) Architecture Overview (diagram description + components)
3) End‑to‑End Workflow (numbered steps)
4) Data Ingestion (validation, extraction, chunking)
5) Embeddings & Vector Store (models, dimensions, persistence, scaling notes)
6) Retrieval Flow (query embedding, similarity search, scoring)
7) RAG Prompting (prompt template, guardrails, finish reasons)
8) UI/Session Management (state, collections, stats)
9) Config & Deploy (env, Dockerfile, docker‑compose, health checks)
10) Observability & Troubleshooting (health_check, common errors, fixes)
11) Performance Tips (chunking, top‑k, model choices)
12) Security & Safety (upload sanitization, API keys, safety settings)
13) Roadmap (future enhancements)

Constraints & Style:
- Audience: mixed engineering/product; level set jargon when needed
- Write concise, skimmable bullets (no paragraphs). Include callouts and gotchas.
- Reference specific file paths (inline) when helpful.
- Close with a 6‑bullet summary and 3 FAQs.

Deliverables:
- Markdown with clear slide sections and bullets
- A Mermaid flowchart block representing the workflow
- A short speaker notes block per major section
"""

Prompt 2 — Generate polished workflow diagrams (PNG/SVG) specs:

"""
System
You are a diagramming expert. Create precise, implementation‑reflective diagrams for a RAG system.

User
Produce: (1) Mermaid flowchart, (2) Mermaid sequence diagram, (3) Graphviz DOT. The diagrams should represent:
- Upload → Validate → Extract → Chunk → Embed → Persist (ChromaDB)
- Query → Embed → Retrieve → Context Prompt → Gemini Answer → Sources
Include node labels that match repo modules (e.g., services/rag_service.py, src/vectorstore.py). Add notes for key parameters: CHUNK_SIZE, CHUNK_OVERLAP, TOP_K_RESULTS. Provide export instructions (Mermaid CLI, VSCode Mermaid, or draw.io import).
"""

Prompt 3 — Convert to PPT (PowerPoint/Google Slides) automatically:

"""
Create a 15–18 slide PPT from the prior outline. For each slide, return:
- Title
- 3–6 bullets
- Optional figure placeholder + caption
- Notes (2–3 sentences)
Also produce a JSON manifest mapping slide → figure type (flowchart/architecture/table) so I can script exports. Use neutral theme colors and minimalism.
"""

Prompt 4 — One‑pager summary (executive PDF handout):

"""
Write a 300–400 word executive brief covering the problem, approach, architecture, and measurable outcomes. Avoid implementation noise; focus on impact and maintainability. End with 3 key risks and 3 mitigations.
"""

---

## 6) Which AI and Design Tools To Use

- Content Generation: ChatGPT (GPT‑4o), Claude 3.5, or Gemini Advanced for drafting slides, summaries, and prompts.
- Diagramming: Mermaid (docs-as-code), Excalidraw (hand‑drawn style), draw.io/diagrams.net, Whimsical or Miro for stakeholder‑friendly visuals.
- PPT Assembly: Microsoft PowerPoint, Google Slides, or Gamma/Tome/Canva for rapid theming. PowerPoint Designer can auto‑layout.
- Exports: Mermaid CLI for PNG/SVG; draw.io export; PowerPoint/Slides to PDF for exec handouts.

Tips
- Keep a single source-of-truth Mermaid block in docs to avoid drift.
- Use repo file paths in labels to improve traceability.
- Test legibility on dark/light backgrounds.

---

## 7) End-to-End Operational Steps (Dev → Prod)

Local (dev)
- Create venv and install deps: `pip install -r requirement.txt`
- Ensure `.env` has `GEMINI_API_KEY`. Start: `streamlit run app.py`
- Upload a PDF; watch logs for chunk/embedding counts; ask queries.

Docker (prod-like)
- Build: `docker compose build`
- Run: `docker compose up -d`
- Volumes persist `data/vector_store` and `data/uploads`. Health check on `/_stcore/health`.

Configuration
- Edit `config.py` or env vars for `EMBEDDING_MODEL`, `CHUNK_SIZE`, `CHUNK_OVERLAP`, `TOP_K_RESULTS`, `GEMINI_MODEL`, `LLM_TEMPERATURE`, `LLM_MAX_TOKENS`.
- Toggle per-session collections: `USE_SESSION_COLLECTIONS=true|false`.

Observability & QA
- Use `RAGService.health_check()` via UI expander to validate embeddings/LLM/vector store.
- Typical fixes: ensure text-based PDFs; adjust chunk size; increase `TOP_K_RESULTS`.

---

## 8) Prompt Template Used in RAGPipeline

The pipeline builds a grounded prompt that instructs Gemini to synthesize across retrieved chunks and cite sources.

Key behaviors
- Analyze all provided context, answer directly, synthesize multiple sources, explain concepts clearly, cite sources.
- Handle insufficient context gracefully (acknowledge gaps instead of hallucinating).

Where
- See: `src/rag_pipeline.py` → `_build_prompt()`.

---

## 9) File Map (for slide references)

- UI: `app.py`
- Config: `config.py`
- Services: `services/document_service.py`, `services/rag_service.py`, `services/session_service.py`
- Core: `src/data_loader.py`, `src/embedding.py`, `src/vectorstore.py`, `src/search.py`, `src/llm.py`, `src/rag_pipeline.py`
- Data: `data/uploads`, `data/vector_store`, `data/pdf`
- Ops: `Dockerfile`, `docker-compose.yml`, `run.sh`, `run.bat`

---

## 10) Slide List (Quick Copy Block)

1. Title & Value Proposition
2. Problem & Requirements
3. Architecture Overview
4. Workflow (End‑to‑End)
5. Document Intake & Validation
6. Chunking Strategy
7. Embeddings: Model & Hardware
8. Vector Store: ChromaDB Persistence
9. Retrieval: Similarity Search & Scoring
10. RAG Prompting & Answer Synthesis
11. UI & Session Management
12. Config, Secrets, and Envs
13. Deployment & Health Checks (Docker)
14. Observability & Troubleshooting
15. Performance & Tuning Playbook
16. Security & Safety Considerations
17. Roadmap & Next Steps
18. Closing Summary + FAQs

---

This file is designed to be pasted into AI tools to produce high‑quality PPTs and workflow diagrams, while staying faithful to this repository’s implementation.


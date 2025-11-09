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

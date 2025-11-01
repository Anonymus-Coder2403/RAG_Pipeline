# GitHub Push Guide - RAG Project

## 📊 Current Situation

Your repository is **>1GB** due to:
- Large PDF files in `data/pdf/`
- Vector store database in `data/vector_store/`
- Virtual environment `.venv/`
- Cached models and binaries

GitHub has a **100MB limit** per file, so we need to exclude large files.

## ✅ What Your .gitignore Already Covers

Good news! Your `.gitignore` already excludes:
- ✅ `.venv/` - Virtual environment
- ✅ `.env` - API keys (IMPORTANT - never commit this!)
- ✅ `data/vector_store/` - Vector database
- ✅ `data/**/*.pdf` - PDF files
- ✅ `data/**/*.bin` - Binary files
- ✅ `__pycache__/` - Python cache

## 📝 Files TO COMMIT (Safe & Essential)

### ✅ Source Code (COMMIT)
```
src/
├── __init__.py
├── data_loader.py
├── embedding.py
├── vectorstore.py
├── search.py
├── llm.py
└── rag_pipeline.py
```

### ✅ Documentation (COMMIT)
```
README.md
GITHUB_PUSH_GUIDE.md
.env.example          # Template only, NOT .env
requirements.txt      # or requirement.txt
pyproject.toml
```

### ✅ Examples & Tests (COMMIT)
```
example.py
test_modules.py
```

### ✅ Notebooks (COMMIT)
```
notebook/document.ipynb
notebook/pdf_loader.ipynb
```

### ✅ Configuration (COMMIT)
```
.gitignore
.gitattributes (if exists)
```

## ❌ Files NOT TO COMMIT (Already Ignored)

### ❌ Environment & Secrets
```
.env                  # Contains API keys - NEVER commit!
.venv/                # Virtual environment
```

### ❌ Large Data Files
```
data/pdf/*.pdf        # User's own PDFs
data/vector_store/    # ChromaDB database
data/text_files/      # User data
```

### ❌ Build Artifacts
```
__pycache__/
*.pyc
*.pyo
dist/
build/
*.egg-info
```

### ❌ OS/Editor Files
```
.DS_Store
Thumbs.db
.vscode/
```

## 🔧 Files to Review/Clean

### ⚠️ Check These Files:
1. **`nul`** - This looks like an error file, should delete
2. **`check.md`** - Keep if useful, otherwise delete
3. **`pdf_loader _reference.ipynb`** - Keep if needed for reference
4. **`test_gemini_setup.py`** - Deleted by user, should be fine

## 📋 Step-by-Step Push Instructions

### Step 1: Clean Up Unnecessary Files
```bash
# Remove error file
rm nul

# (Optional) Remove if not needed
# rm check.md
# rm "pdf_loader _reference.ipynb"
```

### Step 2: Update .gitignore (Add Missing Items)
Your .gitignore is good, but let's add a few more items:

```bash
# Add to .gitignore:
nul
test_gemini_setup.py
```

### Step 3: Check What Will Be Committed
```bash
git status
git add -n .  # Dry run to see what would be added
```

### Step 4: Stage Files for Commit
```bash
# Add all new source files
git add src/

# Add documentation
git add README.md .env.example

# Add examples and tests
git add example.py test_modules.py

# Add modified files
git add notebook/
git add pyproject.toml requirement.txt uv.lock

# If you want to keep check.md
git add check.md

# If you want to keep reference notebook
git add "pdf_loader _reference.ipynb"
```

### Step 5: Commit Changes
```bash
git commit -m "feat: add modular RAG pipeline with Gemini integration

- Add src/ module with clean separation of concerns
- Implement PDFDocumentLoader, EmbeddingManager, VectorStore
- Add RAGRetriever for semantic search
- Integrate Google Gemini 2.5 Flash for answer generation
- Add RAGPipeline orchestrator
- Include example.py and test_modules.py
- Update README with comprehensive documentation"
```

### Step 6: Push to GitHub
```bash
git push origin main
```

## 🚨 If You Get "File Too Large" Error

If you still get errors about large files:

### Option 1: Clean Git History (if large files were committed before)
```bash
# See which large files are in history
git rev-list --objects --all | git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' | sed -n 's/^blob //p' | sort --numeric-sort --key=2 | tail -n 10

# Remove large files from history (CAREFUL!)
git filter-branch --force --index-filter "git rm --cached --ignore-unmatch data/pdf/*.pdf" --prune-empty --tag-name-filter cat -- --all

# Force push (if needed)
git push origin main --force
```

### Option 2: Use Git LFS (Recommended for large files you WANT to track)
```bash
# Install Git LFS
git lfs install

# Track large files (if you want to include some PDFs)
git lfs track "data/pdf/sample.pdf"
git add .gitattributes
git commit -m "chore: add Git LFS tracking"
git push origin main
```

## 📁 Recommended Repository Structure for GitHub

```
RAG/
├── src/                    # ✅ COMMIT - Source code
├── notebook/               # ✅ COMMIT - Development notebooks
├── data/
│   ├── pdf/               # ❌ IGNORE - User PDFs (add .gitkeep)
│   ├── text_files/        # ❌ IGNORE - User data (add .gitkeep)
│   └── vector_store/      # ❌ IGNORE - ChromaDB (add .gitkeep)
├── example.py              # ✅ COMMIT - Usage examples
├── test_modules.py         # ✅ COMMIT - Tests
├── README.md               # ✅ COMMIT - Documentation
├── .env.example            # ✅ COMMIT - Template
├── .gitignore              # ✅ COMMIT - Important!
├── requirements.txt        # ✅ COMMIT - Dependencies
├── pyproject.toml          # ✅ COMMIT - Project config
└── .env                    # ❌ IGNORE - Secrets!
```

## 💡 Pro Tips

### Keep Data Directories (but empty)
Create `.gitkeep` files to preserve directory structure:

```bash
# Create .gitkeep in empty directories
touch data/pdf/.gitkeep
touch data/text_files/.gitkeep
touch data/vector_store/.gitkeep

# Add them to git
git add data/*/.gitkeep
```

### Add Sample Data (Optional)
If you want to include ONE small sample PDF for testing:

```bash
# Add to .gitignore BEFORE the *.pdf line:
# !data/pdf/sample.pdf

# Then add specific file
# git add data/pdf/sample.pdf
```

### Update README with Data Instructions
Add this section to README:

```markdown
## 📥 Setting Up Your Data

This repository does NOT include:
- PDF documents (too large for Git)
- Vector store database (regenerated from your PDFs)

To use this project:
1. Add your PDF files to `data/pdf/`
2. Run the pipeline to generate embeddings
3. The vector store will be created in `data/vector_store/`
```

## ✅ Final Checklist Before Pushing

- [ ] `.env` file is in `.gitignore` (CRITICAL!)
- [ ] No large PDF files being committed
- [ ] No `.venv/` being committed
- [ ] No `__pycache__/` being committed
- [ ] All source code in `src/` is included
- [ ] README.md is updated
- [ ] .env.example is included (without real API key)
- [ ] example.py and test_modules.py are included

## 🎯 Quick Push Command (All-in-One)

```bash
# Clean up
rm nul

# Add everything (gitignore will handle exclusions)
git add .

# Commit
git commit -m "feat: complete modular RAG pipeline with Gemini integration"

# Push
git push origin main
```

## 🆘 Troubleshooting

### Error: "File exceeds GitHub's file size limit"
- Check `.gitignore` is working: `git check-ignore -v <filename>`
- Verify no large files staged: `git ls-files | xargs ls -lh | sort -k5 -hr | head -20`

### Error: "Permission denied (publickey)"
- Set up SSH keys or use HTTPS with token
- `git remote -v` to check remote URL

### Error: "Updates were rejected"
- Pull first: `git pull origin main --rebase`
- Then push: `git push origin main`

---

**Ready to push?** Follow the steps above and your code will be GitHub-ready! 🚀

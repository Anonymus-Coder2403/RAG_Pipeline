#!/bin/bash
# Quick start script for Linux/Mac

echo "========================================"
echo "RAG Chatbot - Production Launch"
echo "========================================"
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "ERROR: .env file not found!"
    echo ""
    echo "Please copy .env.template to .env and add your GEMINI_API_KEY"
    echo ""
    exit 1
fi

# Check if venv exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate venv
echo "Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo ""
echo "Checking dependencies..."
pip install -q -r requirement.txt

# Create directories
mkdir -p data/uploads
mkdir -p data/vector_store

# Launch app
echo ""
echo "========================================"
echo "Starting Streamlit application..."
echo "========================================"
echo ""
echo "Open your browser to: http://localhost:8501"
echo ""

streamlit run app.py

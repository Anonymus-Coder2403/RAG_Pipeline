@echo off
REM Quick start script for Windows

echo ========================================
echo RAG Chatbot - Production Launch
echo ========================================
echo.

REM Check if .env exists
if not exist ".env" (
    echo ERROR: .env file not found!
    echo.
    echo Please copy .env.template to .env and add your GEMINI_API_KEY
    echo.
    pause
    exit /b 1
)

REM Check if venv exists
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
)

REM Activate venv
echo Activating virtual environment...
call .venv\Scripts\activate.bat

REM Install dependencies
echo.
echo Checking dependencies...
pip install -q -r requirement.txt

REM Create directories
if not exist "data\uploads" mkdir data\uploads
if not exist "data\vector_store" mkdir data\vector_store

REM Launch app
echo.
echo ========================================
echo Starting Streamlit application...
echo ========================================
echo.
echo Open your browser to: http://localhost:8501
echo.

streamlit run app.py

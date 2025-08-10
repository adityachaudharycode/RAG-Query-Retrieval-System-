@echo off
echo ========================================
echo LLM-Powered Query-Retrieval System
echo ========================================
echo.

echo Installing dependencies...
python -m pip install -r requirements.txt

echo.
echo Creating directories...
if not exist "data" mkdir data
if not exist "logs" mkdir logs
if not exist "temp" mkdir temp

echo.
echo Setting up environment...
if not exist ".env" (
    if exist ".env.example" (
        copy ".env.example" ".env"
        echo Created .env file from template
        echo.
        echo WARNING: Please edit .env file and add your Gemini API key:
        echo   - GEMINI_API_KEY (for both embeddings and LLM responses)
        echo   See get_api_keys.md for detailed instructions
        echo.
        pause
    )
)

echo.
echo Starting the system...
python main.py

pause

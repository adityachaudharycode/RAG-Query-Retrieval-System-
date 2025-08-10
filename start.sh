#!/bin/bash

echo "========================================"
echo "LLM-Powered Query-Retrieval System"
echo "========================================"
echo

echo "Installing dependencies..."
python3 -m pip install -r requirements.txt

echo
echo "Creating directories..."
mkdir -p data logs temp

echo
echo "Setting up environment..."
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp ".env.example" ".env"
        echo "Created .env file from template"
        echo
        echo "WARNING: Please edit .env file and add your Gemini API key:"
        echo "  - GEMINI_API_KEY (for both embeddings and LLM responses)"
        echo "  See get_api_keys.md for detailed instructions"
        echo
        read -p "Press Enter to continue..."
    fi
fi

echo
echo "Starting the system..."
python3 main.py

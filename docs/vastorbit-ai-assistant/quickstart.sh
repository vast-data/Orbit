#!/bin/bash

# VAST Orbit AI Assistant - Quick Start Script
# This script helps you set up and run the AI assistant

set -e

echo "=========================================="
echo "VAST Orbit AI Assistant - Quick Start"
echo "=========================================="
echo ""

# Check if we're in the right directory
if [ ! -f "backend/app.py" ]; then
    echo "Error: Please run this script from the vastorbit-ai-assistant directory"
    exit 1
fi

# Step 1: Check Python version
echo "[1/6] Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"
echo ""

# Step 2: Install backend dependencies
echo "[2/6] Installing backend dependencies..."
cd backend
pip3 install -r requirements.txt -q
cd ..
echo "✓ Dependencies installed"
echo ""

# Step 3: Check for API key
echo "[3/6] Checking for Anthropic API key..."
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "⚠️  ANTHROPIC_API_KEY not set!"
    echo ""
    echo "Please set your Anthropic API key:"
    echo "  export ANTHROPIC_API_KEY='your_key_here'"
    echo ""
    echo "Get your API key from: https://console.anthropic.com/"
    echo ""
    read -p "Enter your API key now (or press Enter to skip): " api_key
    if [ -n "$api_key" ]; then
        export ANTHROPIC_API_KEY="$api_key"
        echo "✓ API key set for this session"
    else
        echo "⚠️  Continuing without API key (the assistant won't work)"
    fi
else
    echo "✓ ANTHROPIC_API_KEY is set"
fi
echo ""

# Step 4: Set documentation directory
echo "[4/6] Setting documentation directory..."
if [ -z "$VASTORBIT_DOCS_DIR" ]; then
    echo "Please enter the path to your built documentation (HTML output):"
    echo "Example: /home/user/vastorbit/docs/build/html"
    read -p "Path: " docs_dir
    
    if [ -d "$docs_dir" ]; then
        export VASTORBIT_DOCS_DIR="$docs_dir"
        echo "✓ Documentation directory set: $docs_dir"
    else
        echo "⚠️  Directory not found: $docs_dir"
        echo "   The assistant will load 0 documents"
        export VASTORBIT_DOCS_DIR="./docs_content"
    fi
else
    echo "✓ VASTORBIT_DOCS_DIR: $VASTORBIT_DOCS_DIR"
fi
echo ""

# Step 5: Display integration instructions
echo "[5/6] Integration checklist:"
echo ""
echo "To integrate with your Sphinx documentation:"
echo ""
echo "1. Copy frontend files:"
echo "   cp frontend/ai_assistant.css YOUR_DOCS/source/_static/css/"
echo "   cp frontend/ai_assistant.js YOUR_DOCS/source/_static/js/"
echo ""
echo "2. Update conf.py:"
echo "   - Add 'css/ai_assistant.css' to html_css_files"
echo "   - Add html_js_files = ['js/ai_assistant.js']"
echo ""
echo "3. Rebuild your documentation:"
echo "   cd YOUR_DOCS && make html"
echo ""
echo "See INTEGRATION_GUIDE.md for detailed instructions"
echo ""
read -p "Press Enter to continue and start the API server..."

# Step 6: Start the server
echo ""
echo "[6/6] Starting API server..."
echo ""
echo "=========================================="
echo "Server will start on http://localhost:5000"
echo "Press Ctrl+C to stop"
echo "=========================================="
echo ""

cd backend
python3 app.py

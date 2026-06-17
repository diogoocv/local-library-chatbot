#!/bin/bash

echo "======================================"
echo "Installing Local Library Assistant..."
echo "======================================"

echo "[1/3] Creating Python Virtual Environment..."
python3 -m venv venv
source venv/bin/activate

echo "[2/3] Installing Python Backend Dependencies..."
# Ensure you have a requirements.txt in your root folder!
pip install -r requirements.txt

echo "[3/3] Installing Zotero Frontend Dependencies..."
cd client/zotero-plugin
npm install

echo "======================================"
echo "Setup Complete! You can now run ./start-library.sh"
echo "======================================"
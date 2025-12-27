#!/bin/bash
echo "🏗️ Creating database tables..."
python create_tables.py
echo "🚀 Starting FastAPI server..."
uvicorn app.main_simple:app --host 0.0.0.0 --port 8002 --reload
#!/usr/bin/env python
"""
Research Dataset Curator - Integrated Launcher
Combines dataset search, paper parsing, feature analysis, and project curation.
"""

from app_extended import app, init_db

if __name__ == "__main__":
    init_db()
    print("""
    ========================================
    Research Dataset Curator
    ========================================
    
    🚀 Starting application...
    
    📍 Open your browser at:
       - http://127.0.0.1:5000         (Original dataset search)
       - http://127.0.0.1:5000/extended  (Full researcher features)
    
    ✨ Features:
       📄 Parse Papers - Extract dataset refs from PDF research papers
       📊 Feature Analysis - Analyze & select important features
       📋 Curation Projects - Organize & manage curated datasets
       🔍 Dataset Search - Search 6,400+ datasets by model type
    
    Press Ctrl+C to stop the server
    ========================================
    """)
    app.run(debug=True, port=5000)

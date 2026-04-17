#!/usr/bin/env python
"""
Research Dataset Curator - Integrated Launcher
Combines dataset search, paper parsing, feature analysis, and project curation.
"""

import os
from app_extended import app, init_db

if __name__ == "__main__":
    init_db()
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('ENV', 'development') == 'development'
    
    print(f"""
    ========================================
    Research Dataset Curator
    ========================================
    
    🚀 Starting application...
    
    📍 Open your browser at:
       - http://127.0.0.1:{port}         (Original dataset search)
       - http://127.0.0.1:{port}/extended  (Full researcher features)
    
    ✨ Features:
       📄 Parse Papers - Extract dataset refs from PDF research papers
       📊 Feature Analysis - Analyze & select important features
       📋 Curation Projects - Organize & manage curated datasets
       🔍 Dataset Search - Search 6,400+ datasets by model type
    
    Press Ctrl+C to stop the server
    ========================================
    """)
    app.run(debug=debug, port=port, host='0.0.0.0')

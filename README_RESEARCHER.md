# Research Dataset Curator

A comprehensive platform for researchers to find, analyze, and curate datasets for machine learning projects.

## 🎯 Features

### 1. **Dataset Search** (6,400+ datasets)
- Search by ML model type (classification, regression, NLP, computer vision, etc.)
- Filter by domain (tabular, image, text, audio)
- Import from:
  - Hugging Face
  - OpenML
  - Kaggle
  - Custom sources

### 2. **Research Paper Parser** 📄
- Upload PDF research papers
- Automatically extract dataset references and citations
- Find dataset URLs mentioned in papers
- Identify common datasets (MNIST, CIFAR, ImageNet, etc.)

### 3. **Feature Analysis & Selection** 📊
- Upload your dataset (CSV/JSON)
- Analyze feature statistics:
  - Missing values
  - Data types
  - Distribution
  - Correlation
  - Variance
- Automatic feature importance ranking using Random Forest
- Identify features to remove (high missingness, low variance)
- Feature selection suggestions for model optimization

### 4. **Project-Based Curation** 📋
- Create research projects
- Track curated datasets per project
- Save selected features for each dataset
- Add analysis notes
- Export project data
- Search within projects

---

## 🚀 Quick Start

### 1. Install Dependencies

```powershell
cd C:\Users\ASUS\dataset-search-app
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Run the Application

```powershell
python launcher.py
```

### 3. Access the Web Interface

- **Full Features**: http://127.0.0.1:5000/extended
- **Search Only**: http://127.0.0.1:5000

---

## 📖 Usage Guide

### Search for Datasets

1. Go to http://127.0.0.1:5000/extended
2. Click **🔍 Search** tab
3. Select your model type and domain
4. Browse 6,400+ curated datasets
5. Click dataset links to access them

### Parse Research Papers

1. Click **📄 Parse Papers** tab
2. Upload a PDF research paper
3. The system will:
   - Extract text from PDF
   - Find dataset mentions (MNIST, ImageNet, UCI datasets, etc.)
   - Extract dataset URLs
   - List datasets referenced in the paper

### Analyze Dataset Features

1. Click **📊 Analyze Features** tab
2. Upload your dataset (CSV or JSON)
3. Optionally specify target column for supervised learning
4. Get detailed analysis:
   - Feature statistics
   - Correlation analysis
   - Feature importance ranking
   - Recommendations for feature removal
5. View suggestions for optimal feature selection

### Manage Curation Projects

1. Click **📋 Curator Projects** tab
2. Create a new project (e.g., "Image Classification 2026")
3. Add datasets to project
4. Tag selected features per dataset
5. Add analysis notes
6. Export project as JSON for later reference

---

## 🔧 API Endpoints

### Search
- `GET /search?model_type=classification&domain=tabular`

### Paper Parsing
- `POST /api/parse-paper` - Upload and parse PDF

### Feature Analysis
- `POST /api/analyze-dataset` - Upload dataset and analyze

### Projects
- `GET /api/projects` - List all projects
- `POST /api/projects` - Create project
- `GET /api/projects/<id>` - Get project details
- `DELETE /api/projects/<id>` - Delete project
- `POST /api/projects/<id>/datasets` - Add dataset to project
- `GET /api/projects/<id>/stats` - Project statistics

---

## 📊 Supported Formats

### Datasets
- CSV
- JSON

### Papers
- PDF (with text layer)

### Export
- JSON (projects and analysis)

---

## 🎓 Research Workflow

### Typical workflow:
1. **Find Papers** → Read recent research papers in your domain
2. **Parse Papers** → Extract dataset references automatically
3. **Search Datasets** → Browse 6,400+ datasets or use extracted refs
4. **Analyze Datasets** → Select optimal features for your model
5. **Curate** → Organize datasets in projects with feature selections
6. **Export** → Export project data for ML pipeline

---

## 📁 File Structure

```
dataset-search-app/
├── app.py                    # Original search functionality
├── app_extended.py           # Extended researcher features
├── launcher.py               # Main entry point
├── paper_parser.py           # PDF parsing & dataset extraction
├── feature_analyzer.py       # Feature analysis & selection
├── curator.py                # Project management & curation
├── import_datasets.py        # Dataset auto-importer
├── datasets.json             # 6,400+ dataset catalog
├── curator.db                # SQLite project database
├── uploads/                  # Temporary file uploads
└── requirements.txt          # Python dependencies
```

---

## 🔐 Data Privacy

- All processing is local (no data sent to external servers)
- Uploaded files stored in `uploads/` folder
- SQLite database stored locally
- No cloud dependencies for curation

---

## 🚀 Advanced Features

### Import More Datasets
```powershell
python import_datasets.py --openml --query "regression" --limit 50 --append
python import_datasets.py --huggingface --query "nlp" --limit 20 --append
```

### Feature Selection Options
- **Correlation-based**: Find highly correlated features
- **Importance-based**: Use Random Forest feature importance
- **Variance-based**: Remove low-variance features
- **Missing-based**: Remove features with high missingness

### Project Statistics
- Dataset count per project
- Unique datasets tracked
- Feature selections saved
- Analysis notes indexed

---

## 📝 Notes

- Feature analysis uses Random Forest for importance ranking
- Paper parser supports common dataset name patterns
- Datasets can be added to multiple projects
- All data persists locally in SQLite database

---

## 💡 Tips for Researchers

1. **Create projects per research topic** - Keep work organized
2. **Save feature selections** - Reference them for future models
3. **Parse multiple papers** - Discover common datasets in your field
4. **Use feature analysis** - Reduce training time by removing unnecessary features
5. **Export projects** - Share with collaborators (JSON format)

---

## 📞 Support

For issues or feature requests, check the module docstrings:
- `paper_parser.py` - PDF parsing logic
- `feature_analyzer.py` - Statistical analysis
- `curator.py` - Database and project management

---

## 📄 License

Internal research tool for dataset curation and analysis.

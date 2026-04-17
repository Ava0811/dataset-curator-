# Quick Reference - Research Dataset Curator

## Launch the Application

```powershell
cd C:\Users\ASUS\dataset-search-app
.\venv\Scripts\Activate.ps1
python launcher.py
```

Open: http://127.0.0.1:5000/extended

---

## Four Main Tabs

### 1. Search (6,400+ Datasets)
- Select model type and domain
- Browse curated datasets
- Filter by task type
- Direct links to dataset sources

### 2. Parse Papers
- Upload PDF research papers
- Extracts dataset mentions automatically
- Finds URLs to datasets
- Identifies common benchmarks (MNIST, CIFAR, etc.)

### 3. Analyze Features
- Upload CSV or JSON data
- Get feature statistics
- Analyze correlations
- Automatic feature importance ranking
- Suggestions for removing low-value features

### 4. Curator Projects
- Create research projects
- Track datasets per project
- Save selected features
- Add analysis notes
- Export project JSON

---

## Workflow Example

**Goal: Build a text classification model**

1. **Search** → Find text classification datasets
2. **Parse Papers** → Upload 2-3 recent papers, extract referenced datasets
3. **Analyze** → Upload a promising dataset, get feature importance
4. **Curate** → Create project "Text Classification 2026", add datasets with selected features
5. **Export** → Export project JSON to share with team

---

## Key Files

| File | Purpose |
|------|---------|
| `launcher.py` | Main entry point |
| `app_extended.py` | Flask routes for researcher features |
| `paper_parser.py` | PDF parsing & dataset extraction |
| `feature_analyzer.py` | Statistical analysis & feature selection |
| `curator.py` | Project management & SQLite database |
| `datasets.json` | 6,400+ curated datasets |
| `curator.db` | Local project storage |

---

## Common Tasks

### Add More Datasets to Catalog
```powershell
python import_datasets.py --openml --query "clustering" --limit 100 --append
```

### Analyze a Local CSV
- Go to "Analyze Features" tab
- Upload your CSV
- View statistics, correlations, and feature importance

### Create a Research Project
- Click "Curator Projects"
- Enter project name and description
- Add datasets one by one
- Save feature selections per dataset

### Parse a Research Paper
- Click "Parse Papers"
- Upload PDF
- System extracts dataset references
- Click links to find datasets

---

## Tips

- **Feature Analysis**: Upload a sample of your data (10k rows) for faster analysis
- **Paper Parsing**: Works best with PDFs that have extractable text (not scanned images)
- **Projects**: Use descriptive names like "NLP_Classification_v1"
- **Export**: Projects can be exported as JSON and imported later

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Dependencies error | Run: `pip install -r requirements.txt` |
| PDF won't parse | Ensure PDF has text layer (not scan) |
| Feature analysis slow | Reduce dataset sample size or use smaller CSV |
| Database locked | Restart the application |

---

## What's Included

- 6,400+ datasets from OpenML, Kaggle, Hugging Face
- Automatic paper parsing for dataset extraction
- Feature analysis using Random Forest importance
- Project-based curation with SQLite storage
- Full-text search across dataset catalog

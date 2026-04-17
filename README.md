# Dataset Search App

A simple Flask app that helps you find datasets based on the machine learning model type you want to build.

## Features

- Search by model type: classification, regression, clustering, NLP, computer vision, time series
- Filter by domain, task, and minimum dataset size
- View dataset suggestions with links to sources
- API endpoint for programmatic search

## Setup

1. Create a Python virtual environment:

   ```bash
   python -m venv venv
   ```

2. Activate the environment:

   Windows:
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

   macOS / Linux:
   ```bash
   source venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Run

```bash
python app.py
```

Then open `http://127.0.0.1:5000` in your browser.

## Import datasets automatically

A new helper script `import_datasets.py` can pull dataset metadata from public APIs.

Install the updated requirements:

```bash
pip install -r requirements.txt
```

Examples:

```bash
python import_datasets.py --huggingface --query "image" --limit 20 --append
python import_datasets.py --openml --query "classification" --limit 20 --append
python import_datasets.py --kaggle --query "text" --limit 20 --append
```

For Kaggle, you must configure the Kaggle API key first:

1. Install the Kaggle package (already in requirements).
2. Create `kaggle.json` from your Kaggle account.
3. Place it in `%USERPROFILE%\.kaggle\kaggle.json`.

## Extend

- Add more dataset entries to `datasets.json`
- Add UI filters and sorting options
- Connect to a real dataset catalog or search API
- Improve score and ranking logic for better recommendations
- Use `import_datasets.py` to refresh the catalog from Hugging Face, OpenML, and Kaggle

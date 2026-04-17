import re
import os
import json
from pathlib import Path

try:
    import pdfplumber
except ImportError:
    pdfplumber = None

try:
    from PyPDF2 import PdfReader
except ImportError:
    PdfReader = None


def extract_text_from_pdf(pdf_path):
    """Extract text from PDF using pdfplumber or PyPDF2."""
    if pdfplumber and os.path.exists(pdf_path):
        with pdfplumber.open(pdf_path) as pdf:
            text = "\n".join(page.extract_text() or "" for page in pdf.pages)
            return text
    elif PdfReader and os.path.exists(pdf_path):
        reader = PdfReader(pdf_path)
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
        return text
    return ""


def find_dataset_references(text):
    """Find dataset names and URLs mentioned in paper text."""
    datasets = []
    
    # Common dataset name patterns
    patterns = [
        r"(UCI|Kaggle|OpenML|Hugging Face|HuggingFace)\s+dataset[s]?:?\s+([A-Za-z0-9\-_/\.]+)",
        r"dataset\s+named\s+([A-Za-z0-9\-_/\.]+)",
        r"benchmark\s+dataset[s]?:?\s+([A-Za-z0-9\-_/\.]+)",
        r"(ImageNet|MNIST|CIFAR|COCO|Iris|Boston|Adult|Titanic|Wine|Iris|Fashion-MNIST)\b",
    ]
    
    for pattern in patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            name = match.group(-1) if match.lastindex > 1 else match.group(0)
            if name and len(name) > 2:
                datasets.append({"name": name.strip(), "source": "paper"})
    
    # Find URLs that might link to datasets
    url_pattern = r"(https?://[^\s\)]+(?:dataset|data|download)[^\s\)]*)"
    urls = re.findall(url_pattern, text, re.IGNORECASE)
    for url in urls:
        datasets.append({"name": url.split("/")[-1], "url": url, "source": "url"})
    
    return datasets


def parse_paper(pdf_path):
    """Parse a research paper and extract dataset references."""
    if not os.path.exists(pdf_path):
        return {"error": "File not found", "datasets": []}
    
    text = extract_text_from_pdf(pdf_path)
    if not text:
        return {"error": "Could not extract text from PDF", "datasets": []}
    
    datasets = find_dataset_references(text)
    
    return {
        "filename": os.path.basename(pdf_path),
        "text_length": len(text),
        "datasets": datasets,
        "summary": f"Found {len(datasets)} dataset references"
    }


def parse_papers_batch(folder_path):
    """Parse all PDFs in a folder."""
    results = []
    if not os.path.isdir(folder_path):
        return {"error": f"Folder not found: {folder_path}", "results": []}
    
    pdf_files = list(Path(folder_path).glob("*.pdf"))
    for pdf in pdf_files:
        result = parse_paper(str(pdf))
        results.append(result)
    
    return {
        "folder": folder_path,
        "files_processed": len(pdf_files),
        "results": results
    }

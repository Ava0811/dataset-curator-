import argparse
import json
import os
import sys
from datetime import datetime

import requests
from huggingface_hub import HfApi

DATA_FILE = os.path.join(os.path.dirname(__file__), "datasets.json")

DOMAIN_MAP = {
    "image": ["image", "vision", "object-detection", "segmentation"],
    "text": ["text", "nlp", "language", "sentiment", "question-answering"],
    "audio": ["audio", "speech", "sound"],
    "tabular": ["tabular", "csv", "table", "structured"],
    "time series": ["time-series", "timeseries", "forecasting", "anomaly"],
    "video": ["video"],
}

MODEL_TYPE_MAP = {
    "classification": ["classification", "binary", "multiclass", "multilabel"],
    "regression": ["regression", "forecast", "prediction"],
    "nlp": ["nlp", "text", "language"],
    "computer vision": ["vision", "image", "object-detection", "segmentation"],
    "clustering": ["clustering", "unsupervised"],
    "time series": ["time-series", "timeseries", "forecasting", "anomaly"],
}


def safe_lower(value):
    return value.lower() if isinstance(value, str) else ""


def guess_domain(tags, description, name):
    text = " ".join([safe_lower(tags), safe_lower(description), safe_lower(name)])
    for domain, keywords in DOMAIN_MAP.items():
        for keyword in keywords:
            if keyword in text:
                return domain
    return "tabular"


def guess_model_types(tags, description, name):
    text = " ".join([safe_lower(tags), safe_lower(description), safe_lower(name)])
    matched = set()
    for model_type, keywords in MODEL_TYPE_MAP.items():
        for keyword in keywords:
            if keyword in text:
                matched.add(model_type)
    return list(matched or ["classification"])


def normalize_entry(entry):
    return {
        "name": entry.get("name", "Unknown dataset"),
        "domain": entry.get("domain", "tabular"),
        "task": entry.get("task", "unknown"),
        "model_types": entry.get("model_types", ["classification"]),
        "samples": entry.get("samples", 0),
        "labels": entry.get("labels", "unknown"),
        "url": entry.get("url", ""),
        "source": entry.get("source", "external"),
        "license": entry.get("license", "unknown"),
        "updated_at": entry.get("updated_at", datetime.utcnow().isoformat()),
    }


def load_datasets():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_datasets(datasets):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(datasets, f, indent=2, ensure_ascii=False)


def add_unique_datasets(existing, new_items):
    seen_urls = {item.get("url") for item in existing}
    result = list(existing)
    for item in new_items:
        if item.get("url") and item.get("url") not in seen_urls:
            result.append(item)
            seen_urls.add(item.get("url"))
    return result


def fetch_huggingface_datasets(query, limit=20):
    api = HfApi()
    datasets = api.list_datasets(search=query, sort="lastModified", limit=limit, full=True)
    result = []
    for dataset in datasets:
        name = dataset.id
        tags = ", ".join(dataset.tags or [])
        description = dataset.cardData.get("description", "") if getattr(dataset, "cardData", None) else ""
        task = "dataset"
        if getattr(dataset, "cardData", None):
            task = dataset.cardData.get("language") or task
        entry = normalize_entry({
            "name": name,
            "domain": guess_domain(tags, description, name),
            "task": task,
            "model_types": guess_model_types(tags, description, name),
            "samples": 0,
            "labels": ", ".join(dataset.tags or []),
            "url": f"https://huggingface.co/datasets/{name}",
            "source": "huggingface",
            "license": getattr(dataset, "license", "unknown") or "unknown",
        })
        result.append(entry)
    return result


def fetch_openml_datasets(query, limit=20):
    url = "https://www.openml.org/api/v1/json/data/list"
    params = {
        "limit": limit,
        "offset": 0,
        "q": query,
        "status": "active",
    }
    response = requests.get(url, params=params, timeout=20)
    response.raise_for_status()
    data = response.json()
    items = data.get("data_set_description", []) or data.get("data", {}).get("dataset", [])
    result = []
    for item in items:
        instances = item.get("number_of_instances") or item.get("NumberOfInstances")
        if instances is None:
            quality = item.get("quality", [])
            for quality_item in quality:
                if quality_item.get("name") == "NumberOfInstances":
                    instances = quality_item.get("value")
                    break
        try:
            instances = int(instances) if instances is not None else 0
        except (ValueError, TypeError):
            instances = 0

        license_value = item.get("license")
        if isinstance(license_value, dict):
            license_value = license_value.get("name")

        entry = normalize_entry({
            "name": item.get("name", "OpenML dataset"),
            "domain": guess_domain(item.get("tag", ""), item.get("description", ""), item.get("name", "")),
            "task": item.get("data_type", item.get("format", "unknown")),
            "model_types": guess_model_types(item.get("tag", ""), item.get("description", ""), item.get("name", "")),
            "samples": instances,
            "labels": item.get("default_target_attribute") or "unknown",
            "url": f"https://www.openml.org/d/{item.get('did')}",
            "source": "openml",
            "license": license_value or "unknown",
        })
        result.append(entry)
    return result


def fetch_kaggle_datasets(query, limit=20):
    try:
        from kaggle.api.kaggle_api_extended import KaggleApi
    except ImportError:
        print("Kaggle API not installed. Install it with 'pip install kaggle'.")
        return []

    api = KaggleApi()
    try:
        api.authenticate()
    except Exception as exc:
        print(f"Kaggle authentication failed: {exc}")
        return []

    result = []
    datasets = api.dataset_list(search=query, max_size=limit)
    for dataset in datasets:
        entry = normalize_entry({
            "name": f"{dataset.ref}",
            "domain": guess_domain(dataset.title, dataset.subtitle, dataset.ref),
            "task": dataset.subtitle or "dataset",
            "model_types": guess_model_types(dataset.title, dataset.subtitle, dataset.ref),
            "samples": 0,
            "labels": dataset.title,
            "url": f"https://www.kaggle.com/{dataset.ref}",
            "source": "kaggle",
            "license": dataset.license_name or "unknown",
        })
        result.append(entry)
    return result


def parse_arguments():
    parser = argparse.ArgumentParser(description="Import dataset metadata from public dataset catalogs.")
    parser.add_argument("--huggingface", action="store_true", help="Import datasets from Hugging Face")
    parser.add_argument("--openml", action="store_true", help="Import datasets from OpenML")
    parser.add_argument("--kaggle", action="store_true", help="Import datasets from Kaggle")
    parser.add_argument("--query", default="", help="Search query for dataset providers")
    parser.add_argument("--limit", type=int, default=20, help="Maximum number of datasets per source")
    parser.add_argument("--output", default=DATA_FILE, help="Output JSON file")
    parser.add_argument("--append", action="store_true", help="Append imported datasets to existing library")
    return parser.parse_args()


def main():
    args = parse_arguments()
    imported = []

    if args.huggingface:
        imported.extend(fetch_huggingface_datasets(args.query, args.limit))

    if args.openml:
        imported.extend(fetch_openml_datasets(args.query, args.limit))

    if args.kaggle:
        imported.extend(fetch_kaggle_datasets(args.query, args.limit))

    if not imported:
        print("No datasets imported. Use --huggingface, --openml, or --kaggle.")
        sys.exit(0)

    if args.append and os.path.exists(args.output):
        existing = load_datasets()
        datasets = add_unique_datasets(existing, imported)
    else:
        datasets = imported

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(datasets, f, indent=2, ensure_ascii=False)

    print(f"Imported {len(imported)} datasets into {args.output}")


if __name__ == "__main__":
    main()

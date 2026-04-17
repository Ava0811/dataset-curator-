from flask import Flask, request, render_template_string, jsonify
import json
import os

app = Flask(__name__)
DATA_FILE = os.path.join(os.path.dirname(__file__), "datasets.json")

MODEL_TYPE_MAP = {
    "classification": {
        "domains": ["tabular", "image", "text", "audio"],
        "tasks": ["binary", "multiclass", "multilabel"],
    },
    "regression": {
        "domains": ["tabular", "time series"],
        "tasks": ["continuous"],
    },
    "clustering": {
        "domains": ["tabular", "text", "image"],
        "tasks": ["unsupervised"],
    },
    "nlp": {
        "domains": ["text", "audio"],
        "tasks": ["classification", "generation", "qa"],
    },
    "computer vision": {
        "domains": ["image", "video"],
        "tasks": ["classification", "detection", "segmentation"],
    },
    "time series": {
        "domains": ["time series", "tabular"],
        "tasks": ["forecasting", "anomaly detection"],
    },
}

BASE_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Dataset Search</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 2rem; }
    label { display: block; margin-top: 1rem; }
    input, select { width: 100%; max-width: 360px; padding: 0.5rem; margin-top: 0.25rem; }
    button { margin-top: 1rem; padding: 0.75rem 1rem; }
    table { border-collapse: collapse; width: 100%; margin-top: 1.5rem; }
    th, td { border: 1px solid #ccc; padding: 0.75rem; text-align: left; }
    th { background: #f5f5f5; }
    .note { margin-top: 1rem; color: #555; }
  </style>
</head>
<body>
  <h1>Dataset Search for ML Models</h1>
  <form method="get" action="/search">
    <label>Machine learning model type
      <select name="model_type">
        <option value="classification">Classification</option>
        <option value="regression">Regression</option>
        <option value="clustering">Clustering</option>
        <option value="nlp">NLP</option>
        <option value="computer vision">Computer Vision</option>
        <option value="time series">Time Series</option>
      </select>
    </label>
    <label>Preferred domain
      <select name="domain">
        <option value="">Any</option>
        <option value="tabular">Tabular</option>
        <option value="image">Image</option>
        <option value="text">Text</option>
        <option value="audio">Audio</option>
        <option value="time series">Time Series</option>
        <option value="video">Video</option>
      </select>
    </label>
    <label>Task type
      <input type="text" name="task" placeholder="e.g. binary, detection, forecasting" />
    </label>
    <label>Minimum size
      <input type="number" name="min_size" placeholder="Minimum number of examples" />
    </label>
    <button type="submit">Search datasets</button>
  </form>
  {% if results is defined %}
  <div class="note">Found {{ results|length }} datasets that match your preferences.</div>
  <table>
    <thead>
      <tr>
        <th>Name</th>
        <th>Domain</th>
        <th>Task</th>
        <th>Samples</th>
        <th>Labels</th>
        <th>Source</th>
      </tr>
    </thead>
    <tbody>
      {% for dataset in results %}
      <tr>
        <td>{{ dataset.name }}</td>
        <td>{{ dataset.domain }}</td>
        <td>{{ dataset.task }}</td>
        <td>{{ dataset.samples }}</td>
        <td>{{ dataset.labels }}</td>
        <td><a href="{{ dataset.url }}" target="_blank">Open</a></td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
  {% endif %}
</body>
</html>
"""


def load_datasets():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def score_dataset(dataset, model_type, domain, task, min_size):
    score = 0
    if model_type and dataset["model_types"] and model_type in dataset["model_types"]:
        score += 3
    if domain and dataset["domain"] == domain:
        score += 2
    if task and task.lower() in dataset["task"].lower():
        score += 2
    if min_size and dataset["samples"] >= min_size:
        score += 1
    return score


def search_datasets(model_type, domain, task, min_size):
    datasets = load_datasets()
    results = []
    for dataset in datasets:
        if model_type and model_type not in dataset["model_types"]:
            continue
        if domain and dataset["domain"] != domain:
            continue
        if task and task.lower() not in dataset["task"].lower():
            continue
        if min_size and dataset["samples"] < min_size:
            continue
        results.append(dataset)
    return sorted(results, key=lambda d: score_dataset(d, model_type, domain, task, min_size), reverse=True)


@app.route("/")
def home():
    return render_template_string(BASE_TEMPLATE)


@app.route("/search")
def search():
    model_type = request.args.get("model_type", "classification")
    domain = request.args.get("domain", "").strip().lower()
    task = request.args.get("task", "").strip().lower()
    min_size = request.args.get("min_size", "")
    try:
        min_size = int(min_size) if min_size else 0
    except ValueError:
        min_size = 0

    results = search_datasets(model_type, domain, task, min_size)
    return render_template_string(BASE_TEMPLATE, results=results)


@app.route("/api/search")
def api_search():
    model_type = request.args.get("model_type", "classification")
    domain = request.args.get("domain", "").strip().lower()
    task = request.args.get("task", "").strip().lower()
    min_size = request.args.get("min_size", "")
    try:
        min_size = int(min_size) if min_size else 0
    except ValueError:
        min_size = 0

    results = search_datasets(model_type, domain, task, min_size)
    return jsonify(results)


if __name__ == "__main__":
    app.run(debug=True, port=5000)

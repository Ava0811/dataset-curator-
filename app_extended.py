from flask import Flask, request, render_template_string, jsonify, send_file
import json
import os
from werkzeug.utils import secure_filename

from app import app, load_datasets, search_datasets, DATA_FILE, BASE_TEMPLATE, MODEL_TYPE_MAP
from paper_parser import parse_paper, find_dataset_references
from feature_analyzer import load_dataset, analyze_features, suggest_features, export_feature_report
from curator import (
    init_db, create_project, list_projects, get_project, add_dataset_to_project,
    export_project, delete_project, search_datasets_in_project, get_statistics
)

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

EXTENDED_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Research Dataset Curator</title>
  <style>
    * { box-sizing: border-box; }
    body { font-family: Arial, sans-serif; margin: 0; background: #f5f5f5; }
    .nav { background: #333; color: white; padding: 1rem; display: flex; gap: 1rem; }
    .nav button { background: #555; color: white; border: none; padding: 0.5rem 1rem; cursor: pointer; border-radius: 3px; }
    .nav button.active { background: #007bff; }
    .container { max-width: 1200px; margin: 2rem auto; padding: 0 1rem; }
    .tab { display: none; }
    .tab.active { display: block; }
    label { display: block; margin-top: 1rem; font-weight: bold; }
    input[type="text"], input[type="number"], select, textarea { width: 100%; max-width: 500px; padding: 0.5rem; margin-top: 0.25rem; }
    textarea { height: 100px; }
    button { background: #007bff; color: white; padding: 0.75rem 1.5rem; border: none; cursor: pointer; border-radius: 3px; }
    button:hover { background: #0056b3; }
    .card { background: white; padding: 1.5rem; margin: 1rem 0; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
    table { width: 100%; border-collapse: collapse; margin: 1rem 0; }
    th, td { border: 1px solid #ddd; padding: 0.75rem; text-align: left; }
    th { background: #f5f5f5; font-weight: bold; }
    .success { color: green; }
    .error { color: red; }
    .analysis-result { background: #f0f8ff; padding: 1rem; border-radius: 3px; margin: 1rem 0; }
  </style>
  <script>
    function showTab(tabName) {
      document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
      document.getElementById(tabName).classList.add('active');
      document.querySelectorAll('.nav button').forEach(b => b.classList.remove('active'));
      event.target.classList.add('active');
    }
  </script>
</head>
<body>
  <div class="nav">
    <button class="active" onclick="showTab('search')">🔍 Search</button>
    <button onclick="showTab('papers')">📄 Parse Papers</button>
    <button onclick="showTab('analyze')">📊 Analyze Features</button>
    <button onclick="showTab('curator')">📋 Curator Projects</button>
  </div>

  <div class="container">
    <!-- Search Tab -->
    <div id="search" class="tab active">
      <h2>Dataset Search</h2>
      <form method="get" action="/search">
        <label>Model Type
          <select name="model_type">
            <option value="classification">Classification</option>
            <option value="regression">Regression</option>
            <option value="clustering">Clustering</option>
            <option value="nlp">NLP</option>
            <option value="computer vision">Computer Vision</option>
            <option value="time series">Time Series</option>
          </select>
        </label>
        <label>Domain
          <select name="domain">
            <option value="">Any</option>
            <option value="tabular">Tabular</option>
            <option value="image">Image</option>
            <option value="text">Text</option>
          </select>
        </label>
        <button type="submit">Search</button>
      </form>
    </div>

    <!-- Papers Tab -->
    <div id="papers" class="tab">
      <h2>Parse Research Papers</h2>
      <form action="/api/parse-paper" method="post" enctype="multipart/form-data">
        <label>Upload PDF
          <input type="file" name="paper" accept=".pdf" required>
        </label>
        <button type="submit">Parse Paper</button>
      </form>
      <div id="paper-results"></div>
    </div>

    <!-- Feature Analysis Tab -->
    <div id="analyze" class="tab">
      <h2>Feature Analysis & Selection</h2>
      <form action="/api/analyze-dataset" method="post" enctype="multipart/form-data">
        <label>Upload Dataset (CSV/JSON)
          <input type="file" name="dataset" accept=".csv,.json" required>
        </label>
        <label>Target Column (optional)
          <input type="text" name="target" placeholder="e.g., target, label, y">
        </label>
        <button type="submit">Analyze</button>
      </form>
      <div id="analysis-results"></div>
    </div>

    <!-- Curator Tab -->
    <div id="curator" class="tab">
      <h2>Curation Projects</h2>
      <div class="card">
        <h3>Create New Project</h3>
        <form id="create-project">
          <label>Project Name
            <input type="text" id="project-name" required>
          </label>
          <label>Description
            <textarea id="project-desc"></textarea>
          </label>
          <button type="button" onclick="createProject()">Create</button>
        </form>
      </div>
      <div id="projects-list"></div>
    </div>
  </div>

  <script>
    async function createProject() {
      const name = document.getElementById('project-name').value;
      const desc = document.getElementById('project-desc').value;
      const res = await fetch('/api/projects', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, description: desc })
      });
      const data = await res.json();
      alert(data.status || data.error);
      loadProjects();
    }

    async function loadProjects() {
      const res = await fetch('/api/projects');
      const data = await res.json();
      const html = data.projects.map(p => `
        <div class="card">
          <h3>${p.name}</h3>
          <p>${p.description}</p>
          <button onclick="viewProject(${p.id})">View</button>
          <button onclick="deleteProject(${p.id})">Delete</button>
        </div>
      `).join('');
      document.getElementById('projects-list').innerHTML = html;
    }

    function viewProject(id) {
      window.location.href = '/project/' + id;
    }

    async function deleteProject(id) {
      if (confirm('Delete this project?')) {
        await fetch('/api/projects/' + id, { method: 'DELETE' });
        loadProjects();
      }
    }

    loadProjects();
  </script>
</body>
</html>
"""


@app.route("/extended")
def extended_ui():
    return render_template_string(EXTENDED_TEMPLATE)


@app.route("/api/parse-paper", methods=["POST"])
def api_parse_paper():
    if "paper" not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files["paper"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400
    
    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    
    result = parse_paper(filepath)
    return jsonify(result)


@app.route("/api/analyze-dataset", methods=["POST"])
def api_analyze_dataset():
    if "dataset" not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files["dataset"]
    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    
    df, error = load_dataset(filepath)
    if error:
        return jsonify(error), 400
    
    target = request.form.get("target")
    analysis = analyze_features(df)
    suggestions = suggest_features(df, target)
    
    return jsonify({
        "analysis": analysis,
        "suggestions": suggestions
    })


@app.route("/api/projects", methods=["GET", "POST"])
def api_projects():
    if request.method == "POST":
        data = request.get_json()
        result = create_project(data.get("name"), data.get("description", ""))
        return jsonify(result)
    else:
        return jsonify(list_projects())


@app.route("/api/projects/<int:project_id>", methods=["GET", "DELETE"])
def api_project(project_id):
    if request.method == "GET":
        return jsonify(get_project(project_id))
    elif request.method == "DELETE":
        result = delete_project(project_id)
        return jsonify(result)


@app.route("/api/projects/<int:project_id>/datasets", methods=["POST"])
def api_add_dataset(project_id):
    data = request.get_json()
    result = add_dataset_to_project(
        project_id,
        data.get("dataset_name"),
        data.get("dataset_url"),
        data.get("selected_features"),
        data.get("notes", "")
    )
    return jsonify(result)


@app.route("/api/projects/<int:project_id>/stats")
def api_project_stats(project_id):
    stats = get_statistics(project_id)
    return jsonify(stats)


@app.route("/project/<int:project_id>")
def view_project(project_id):
    project_data = get_project(project_id)
    
    project_template = """
    <!doctype html>
    <html>
    <head>
      <title>Project: {{ project.name }}</title>
      <style>
        body { font-family: Arial; margin: 2rem; }
        .card { background: #f5f5f5; padding: 1rem; margin: 1rem 0; border-radius: 5px; }
        button { background: #007bff; color: white; padding: 0.5rem 1rem; border: none; cursor: pointer; }
        table { width: 100%; border-collapse: collapse; }
        th, td { border: 1px solid #ddd; padding: 0.75rem; text-align: left; }
      </style>
    </head>
    <body>
      <h1>{{ project.name }}</h1>
      <p>{{ project.description }}</p>
      <button onclick="window.history.back()">Back</button>
      <h2>Curated Datasets</h2>
      <table>
        <tr>
          <th>Dataset</th>
          <th>Features</th>
          <th>Notes</th>
          <th>Added</th>
        </tr>
        {% for dataset in datasets %}
        <tr>
          <td><a href="{{ dataset.dataset_url }}" target="_blank">{{ dataset.dataset_name }}</a></td>
          <td>{{ dataset.selected_features }}</td>
          <td>{{ dataset.analysis_notes }}</td>
          <td>{{ dataset.added_at }}</td>
        </tr>
        {% endfor %}
      </table>
    </body>
    </html>
    """
    
    from flask import render_template_string
    return render_template_string(project_template, project=project_data["project"], datasets=project_data["datasets"])


if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000)

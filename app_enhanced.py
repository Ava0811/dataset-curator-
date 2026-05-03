from flask import Flask, request, render_template_string, jsonify
import json
import os
from llm_integration import get_smart_recommendations, get_dataset_description

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

# Enhanced template with AI features
BASE_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Dataset Search - AI Powered</title>
  <style>
    body { 
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      margin: 2rem;
      max-width: 1200px;
      margin-left: auto;
      margin-right: auto;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      min-height: 100vh;
      padding: 2rem 0;
    }
    .container {
      background: white;
      border-radius: 10px;
      padding: 2rem;
      box-shadow: 0 10px 40px rgba(0,0,0,0.2);
    }
    h1 { 
      color: #333;
      border-bottom: 3px solid #667eea;
      padding-bottom: 0.5rem;
    }
    .section {
      margin-top: 2rem;
      padding-top: 2rem;
      border-top: 2px solid #eee;
    }
    .ai-badge {
      display: inline-block;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      padding: 0.3rem 0.8rem;
      border-radius: 20px;
      font-size: 0.8rem;
      font-weight: bold;
      margin-left: 0.5rem;
    }
    label { 
      display: block;
      margin-top: 1rem;
      font-weight: 500;
      color: #333;
    }
    input, select, textarea { 
      width: 100%; 
      max-width: 100%;
      padding: 0.75rem; 
      margin-top: 0.25rem;
      border: 2px solid #ddd;
      border-radius: 5px;
      font-size: 1rem;
      box-sizing: border-box;
    }
    input:focus, select:focus, textarea:focus {
      outline: none;
      border-color: #667eea;
      box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    textarea {
      resize: vertical;
      min-height: 100px;
    }
    button { 
      margin-top: 1rem;
      margin-right: 0.5rem;
      padding: 0.75rem 1.5rem;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      border: none;
      border-radius: 5px;
      cursor: pointer;
      font-weight: bold;
      font-size: 1rem;
      transition: transform 0.2s;
    }
    button:hover {
      transform: translateY(-2px);
      box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
    }
    button.secondary {
      background: #f0f0f0;
      color: #333;
    }
    button.secondary:hover {
      background: #e0e0e0;
    }
    .ai-recommendations {
      background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
      border-left: 4px solid #667eea;
      padding: 1.5rem;
      border-radius: 5px;
      margin-top: 1.5rem;
    }
    .ai-recommendations h3 {
      color: #667eea;
      margin-top: 0;
    }
    .recommendation-item {
      background: white;
      padding: 1rem;
      margin: 0.5rem 0;
      border-radius: 5px;
      border-left: 3px solid #764ba2;
    }
    .recommendation-item strong {
      color: #764ba2;
    }
    table { 
      border-collapse: collapse; 
      width: 100%; 
      margin-top: 1.5rem;
    }
    th, td { 
      border: 1px solid #ddd; 
      padding: 1rem; 
      text-align: left;
    }
    th { 
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      font-weight: bold;
    }
    tr:hover {
      background: #f9f9f9;
    }
    td a {
      color: #667eea;
      text-decoration: none;
      font-weight: bold;
    }
    td a:hover {
      text-decoration: underline;
    }
    .note { 
      margin-top: 1rem; 
      color: #666;
      background: #f9f9f9;
      padding: 1rem;
      border-radius: 5px;
      border-left: 3px solid #667eea;
    }
    .tabs {
      display: flex;
      gap: 0.5rem;
      margin-top: 1rem;
      flex-wrap: wrap;
    }
    .tab-button {
      padding: 0.5rem 1rem;
      background: #f0f0f0;
      border: 2px solid #ddd;
      border-radius: 5px;
      cursor: pointer;
      transition: all 0.3s;
    }
    .tab-button.active {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      border-color: #667eea;
    }
    .tab-content {
      display: none;
      margin-top: 1.5rem;
    }
    .tab-content.active {
      display: block;
    }
    .dataset-description {
      font-style: italic;
      color: #555;
      margin-top: 0.5rem;
    }
    .loading {
      display: inline-block;
      width: 20px;
      height: 20px;
      border: 3px solid #f3f3f3;
      border-top: 3px solid #667eea;
      border-radius: 50%;
      animation: spin 1s linear infinite;
    }
    @keyframes spin {
      0% { transform: rotate(0deg); }
      100% { transform: rotate(360deg); }
    }
  </style>
</head>
<body>
  <div class="container">
    <h1>🤖 AI-Powered Dataset Curator <span class="ai-badge">LLM Enhanced</span></h1>
    
    <div class="tabs">
      <button class="tab-button active" onclick="switchTab('smart')">Smart Recommendations</button>
      <button class="tab-button" onclick="switchTab('traditional')">Traditional Search</button>
    </div>

    <!-- Smart AI Recommendations Tab -->
    <div id="smart" class="tab-content active">
      <div class="section">
        <h2>Describe Your ML Problem <span class="ai-badge">AI</span></h2>
        <p>Tell us about your machine learning project, and our AI will recommend the best datasets for your use case.</p>
        
        <form method="post" action="/ai-recommend">
          <label>What's your ML project about?
            <textarea name="user_problem" placeholder="e.g., I want to build a model to classify images of different dog breeds, or detect anomalies in time series sensor data" required></textarea>
          </label>
          <label>Select LLM Provider (optional)
            <select name="provider">
              <option value="">Auto-detect (recommended)</option>
              <option value="openai">OpenAI GPT</option>
              <option value="anthropic">Anthropic Claude</option>
              <option value="huggingface">Hugging Face</option>
              <option value="fallback">Fallback (template-based)</option>
            </select>
          </label>
          <button type="submit">Get AI Recommendations 🚀</button>
        </form>

        {% if ai_recommendations is defined and ai_recommendations %}
        <div class="ai-recommendations">
          <h3>✨ AI-Powered Recommendations</h3>
          
          {% if ai_recommendations.get('error') %}
            <p style="color: #d32f2f;">{{ ai_recommendations['error'] }}</p>
          {% else %}
            <h4>Top Recommended Datasets:</h4>
            {% for dataset_name in ai_recommendations.get('top_recommendations', []) %}
              <div class="recommendation-item">
                <strong>{{ dataset_name }}</strong>
                <p>{{ ai_recommendations.get('reasoning', 'Dataset recommended for your use case') }}</p>
              </div>
            {% endfor %}
            
            {% if ai_recommendations.get('tips') %}
            <h4>💡 Tips:</h4>
            <p>{{ ai_recommendations['tips'] }}</p>
            {% endif %}
          {% endif %}
        </div>
        {% endif %}
      </div>
    </div>

    <!-- Traditional Search Tab -->
    <div id="traditional" class="tab-content">
      <div class="section">
        <h2>Traditional Filters</h2>
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
              <th>Description</th>
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
              <td class="dataset-description">{{ dataset.get('ai_description', dataset.get('description', 'High-quality dataset for ML projects')) }}</td>
              <td><a href="{{ dataset.url }}" target="_blank">Open →</a></td>
            </tr>
            {% endfor %}
          </tbody>
        </table>
        {% endif %}
      </div>
    </div>
  </div>

  <script>
    function switchTab(tabName) {
      // Hide all tabs
      var tabs = document.querySelectorAll('.tab-content');
      tabs.forEach(function(tab) {
        tab.classList.remove('active');
      });
      
      // Remove active class from all buttons
      var buttons = document.querySelectorAll('.tab-button');
      buttons.forEach(function(btn) {
        btn.classList.remove('active');
      });
      
      // Show selected tab
      document.getElementById(tabName).classList.add('active');
      
      // Add active class to clicked button
      event.target.classList.add('active');
    }
  </script>
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
    
    # Generate AI descriptions for datasets
    for dataset in results:
        try:
            dataset['ai_description'] = get_dataset_description(dataset, use_cache=True)
        except Exception as e:
            dataset['ai_description'] = dataset.get('description', 'High-quality dataset for ML projects')
    
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


@app.route("/ai-recommend", methods=["POST"])
def ai_recommend():
    """Endpoint for AI-powered recommendations"""
    user_problem = request.form.get("user_problem", "").strip()
    provider = request.form.get("provider", None)
    
    if not user_problem:
        return render_template_string(BASE_TEMPLATE, ai_recommendations={"error": "Please describe your ML problem"})
    
    # Get all datasets
    datasets = load_datasets()
    
    # Get AI recommendations
    ai_recommendations = get_smart_recommendations(user_problem, datasets, provider=provider if provider else None)
    
    return render_template_string(BASE_TEMPLATE, ai_recommendations=ai_recommendations)


@app.route("/api/ai-recommend", methods=["POST"])
def api_ai_recommend():
    """API endpoint for AI-powered recommendations"""
    data = request.get_json()
    user_problem = data.get("user_problem", "").strip()
    provider = data.get("provider", None)
    
    if not user_problem:
        return jsonify({"error": "Please describe your ML problem"}), 400
    
    datasets = load_datasets()
    ai_recommendations = get_smart_recommendations(user_problem, datasets, provider=provider if provider else None)
    
    return jsonify(ai_recommendations)


if __name__ == "__main__":
    app.run(debug=True, port=5000)

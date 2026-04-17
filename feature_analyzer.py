import json
import numpy as np
import pandas as pd
from pathlib import Path

try:
    from sklearn.feature_selection import mutual_info_classif, mutual_info_regression
    from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
    from sklearn.preprocessing import LabelEncoder
except ImportError:
    pass


def load_dataset(file_path, sample_size=None):
    """Load dataset from CSV or JSON."""
    if not Path(file_path).exists():
        return None, {"error": f"File not found: {file_path}"}
    
    try:
        if file_path.endswith(".csv"):
            df = pd.read_csv(file_path)
        elif file_path.endswith(".json"):
            df = pd.read_json(file_path)
        else:
            return None, {"error": "Unsupported file format. Use CSV or JSON."}
        
        if sample_size and len(df) > sample_size:
            df = df.sample(n=sample_size)
        
        return df, None
    except Exception as e:
        return None, {"error": str(e)}


def analyze_features(df):
    """Analyze dataset features."""
    if df is None or df.empty:
        return {"error": "Dataset is empty"}
    
    analysis = {
        "shape": df.shape,
        "columns": len(df.columns),
        "rows": len(df),
        "features": {}
    }
    
    for col in df.columns:
        col_analysis = {
            "dtype": str(df[col].dtype),
            "non_null": df[col].notna().sum(),
            "missing": df[col].isna().sum(),
            "unique": df[col].nunique(),
        }
        
        if pd.api.types.is_numeric_dtype(df[col]):
            col_analysis.update({
                "mean": float(df[col].mean()),
                "std": float(df[col].std()),
                "min": float(df[col].min()),
                "max": float(df[col].max()),
                "median": float(df[col].median()),
            })
        elif pd.api.types.is_categorical_dtype(df[col]) or df[col].nunique() < 20:
            col_analysis["top_values"] = df[col].value_counts().head(5).to_dict()
        
        analysis["features"][col] = col_analysis
    
    return analysis


def calculate_feature_correlation(df, target_col=None):
    """Calculate feature correlations."""
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    
    if len(numeric_cols) < 2:
        return {"error": "Not enough numeric features for correlation analysis"}
    
    correlation = {
        "method": "pearson",
        "correlations": {}
    }
    
    corr_matrix = df[numeric_cols].corr()
    
    if target_col and target_col in numeric_cols:
        target_corr = corr_matrix[target_col].sort_values(ascending=False)
        correlation["target_correlations"] = target_corr.to_dict()
    
    return correlation


def select_features_by_importance(df, target_col, task_type="classification", top_k=10):
    """Select top features using Random Forest importance."""
    if target_col not in df.columns:
        return {"error": f"Target column '{target_col}' not found"}
    
    X = df.drop(columns=[target_col])
    y = df[target_col]
    
    # Encode categorical features
    X_encoded = X.copy()
    label_encoders = {}
    for col in X_encoded.columns:
        if X_encoded[col].dtype == 'object':
            le = LabelEncoder()
            X_encoded[col] = le.fit_transform(X_encoded[col].astype(str))
            label_encoders[col] = le
    
    # Train model based on task type
    if task_type == "classification":
        model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    else:
        model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    
    model.fit(X_encoded, y)
    
    # Get feature importance
    importances = model.feature_importances_
    feature_names = X_encoded.columns
    
    # Sort by importance
    indices = np.argsort(importances)[::-1][:top_k]
    
    result = {
        "task_type": task_type,
        "top_features": [],
        "importances": {}
    }
    
    for idx in indices:
        fname = feature_names[idx]
        importance = float(importances[idx])
        result["top_features"].append(fname)
        result["importances"][fname] = importance
    
    return result


def suggest_features(df, target_col=None, top_k=10):
    """Suggest important features for analysis."""
    if df is None or df.empty:
        return {"error": "Dataset is empty"}
    
    suggestions = {
        "analysis": analyze_features(df),
        "correlation": calculate_feature_correlation(df, target_col),
        "selected_features": []
    }
    
    # Remove highly missing columns
    missing_threshold = 0.5
    for col in df.columns:
        missing_ratio = df[col].isna().sum() / len(df)
        if missing_ratio > missing_threshold:
            suggestions["selected_features"].append({
                "feature": col,
                "reason": f"High missing ratio: {missing_ratio:.2%}",
                "recommended_action": "remove"
            })
    
    # Identify numeric features with low variance
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        if df[col].var() < 1e-10:
            suggestions["selected_features"].append({
                "feature": col,
                "reason": "Very low variance",
                "recommended_action": "remove"
            })
    
    return suggestions


def export_feature_report(analysis, output_path):
    """Export feature analysis report."""
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(analysis, f, indent=2, default=str)

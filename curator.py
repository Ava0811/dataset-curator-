import json
import os
import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = os.path.join(os.path.dirname(__file__), "curator.db")


def init_db():
    """Initialize SQLite database for curation projects."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Projects table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Curated datasets table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS curated_datasets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            dataset_name TEXT NOT NULL,
            dataset_url TEXT,
            selected_features TEXT,
            analysis_notes TEXT,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id)
        )
    """)
    
    conn.commit()
    conn.close()


def create_project(name, description=""):
    """Create a new curation project."""
    init_db()
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO projects (name, description) VALUES (?, ?)",
            (name, description)
        )
        conn.commit()
        project_id = cursor.lastrowid
        conn.close()
        return {"id": project_id, "name": name, "status": "created"}
    except sqlite3.IntegrityError:
        return {"error": f"Project '{name}' already exists"}


def list_projects():
    """List all curation projects."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM projects ORDER BY updated_at DESC")
    projects = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return {"projects": projects}


def get_project(project_id):
    """Get project details."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
    project = dict(cursor.fetchone() or {})
    
    cursor.execute("SELECT * FROM curated_datasets WHERE project_id = ? ORDER BY added_at DESC", (project_id,))
    datasets = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return {"project": project, "datasets": datasets}


def add_dataset_to_project(project_id, dataset_name, dataset_url, selected_features=None, notes=""):
    """Add a curated dataset to a project."""
    init_db()
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO curated_datasets 
               (project_id, dataset_name, dataset_url, selected_features, analysis_notes)
               VALUES (?, ?, ?, ?, ?)""",
            (project_id, dataset_name, dataset_url, json.dumps(selected_features or []), notes)
        )
        conn.commit()
        dataset_id = cursor.lastrowid
        conn.close()
        return {"id": dataset_id, "status": "added"}
    except Exception as e:
        return {"error": str(e)}


def export_project(project_id, output_path):
    """Export project and its curated datasets."""
    project_data = get_project(project_id)
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(project_data, f, indent=2, default=str)
    
    return {"status": "exported", "file": output_path}


def delete_project(project_id):
    """Delete a project and its datasets."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM curated_datasets WHERE project_id = ?", (project_id,))
    cursor.execute("DELETE FROM projects WHERE id = ?", (project_id,))
    conn.commit()
    conn.close()
    return {"status": "deleted"}


def search_datasets_in_project(project_id, query):
    """Search curated datasets within a project."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(
        """SELECT * FROM curated_datasets 
           WHERE project_id = ? AND (dataset_name LIKE ? OR analysis_notes LIKE ?)
           ORDER BY added_at DESC""",
        (project_id, f"%{query}%", f"%{query}%")
    )
    datasets = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return {"results": datasets}


def get_statistics(project_id):
    """Get project statistics."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM curated_datasets WHERE project_id = ?", (project_id,))
    dataset_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(DISTINCT dataset_url) FROM curated_datasets WHERE project_id = ?", (project_id,))
    unique_datasets = cursor.fetchone()[0]
    
    conn.close()
    return {
        "project_id": project_id,
        "total_curations": dataset_count,
        "unique_datasets": unique_datasets
    }

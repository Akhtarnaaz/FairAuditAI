import sqlite3
import os
import shutil
from pathlib import Path

BASE_DIR = Path("d:/Personal_projects/Detect_bias")
BACKEND_DIR = BASE_DIR / "backend"
UPLOADS_DIR = BACKEND_DIR / "uploads"
DB_PATH = BACKEND_DIR / "bias_auditor.db"

def cleanup():
    print("Starting cleanup of demo data...")
    
    # 1. Clear Database
    if DB_PATH.exists():
        print(f"Clearing database: {DB_PATH}")
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        tables = [
            "fairness_scores", 
            "bias_explanations", 
            "mitigation_recommendations", 
            "audit_reports",
            "audit_runs", 
            "models", 
            "datasets"
        ]
        
        for table in tables:
            try:
                cursor.execute(f"DELETE FROM {table}")
                print(f" - Cleared table: {table}")
            except sqlite3.OperationalError as e:
                print(f" - Table {table} not found or error: {e}")
        
        conn.commit()
        conn.close()
    else:
        print("Database not found.")

    # 2. Clear Uploads
    if UPLOADS_DIR.exists():
        print(f"Clearing uploads directory: {UPLOADS_DIR}")
        for folder in ["models", "datasets"]:
            folder_path = UPLOADS_DIR / folder
            if folder_path.exists():
                for item in folder_path.iterdir():
                    if item.is_file():
                        item.unlink()
                        print(f" - Deleted file: {item.name}")
    
    # 3. Remove Demo Directories
    for demo_dir in ["demo", "demo_downloads"]:
        path = BASE_DIR / demo_dir
        if path.exists():
            print(f"Removing demo directory: {path}")
            shutil.rmtree(path)
            print(f" - Deleted directory: {demo_dir}")

    # 4. Remove temporary scripts
    for script in ["test_query.py", "generate_multi_domain_demos.py"]:
        path = BASE_DIR / script
        if path.exists():
            path.unlink()
            print(f" - Deleted script: {script}")
    
    backend_script = BACKEND_DIR / "test_query.py"
    if backend_script.exists():
        backend_script.unlink()
        print(f" - Deleted script: backend/test_query.py")

    print("\nCleanup complete! You have a clean slate.")

if __name__ == "__main__":
    cleanup()

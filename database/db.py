import sqlite3
from pathlib import Path
from flask import current_app, g
def get_db():
    if "db" not in g:
        path = Path(current_app.config["DATABASE"])
        path.parent.mkdir(parents=True, exist_ok=True)
        g.db = sqlite3.connect(path)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys=ON")
    return g.db
def close_db(_error=None):
    db = g.pop("db", None)
    if db is not None: db.close()
def init_db():
    db = get_db()
    db.executescript("""
    CREATE TABLE IF NOT EXISTS machines(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT NOT NULL UNIQUE,created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
    CREATE TABLE IF NOT EXISTS baselines(id INTEGER PRIMARY KEY AUTOINCREMENT,machine_id INTEGER NOT NULL UNIQUE,model BLOB NOT NULL,sample_count INTEGER NOT NULL,created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,FOREIGN KEY(machine_id) REFERENCES machines(id) ON DELETE CASCADE);
    CREATE TABLE IF NOT EXISTS analyses(id INTEGER PRIMARY KEY AUTOINCREMENT,machine_id INTEGER NOT NULL,filename TEXT NOT NULL,result TEXT NOT NULL,anomaly_score REAL NOT NULL,health_score REAL NOT NULL,features TEXT NOT NULL,created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,FOREIGN KEY(machine_id) REFERENCES machines(id) ON DELETE CASCADE);
    """)
    db.commit()

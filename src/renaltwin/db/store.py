import sqlite3, json, os
from pathlib import Path
from contextlib import contextmanager
from datetime import datetime, timezone

def db_path():
    p=Path(os.getenv("RT_DB_PATH","artifacts/renaltwin.db"));p.parent.mkdir(parents=True,exist_ok=True);return p
@contextmanager
def connect():
    c=sqlite3.connect(db_path());c.row_factory=sqlite3.Row;c.execute("PRAGMA foreign_keys=ON");
    try: yield c; c.commit()
    finally: c.close()
def init_db():
    with connect() as c:
        c.executescript('''
        CREATE TABLE IF NOT EXISTS twins(twin_id TEXT PRIMARY KEY, display_name TEXT NOT NULL, age INTEGER NOT NULL, sex TEXT NOT NULL, diabetes INTEGER NOT NULL, hypertension INTEGER NOT NULL, cvd INTEGER NOT NULL DEFAULT 0, data_origin TEXT NOT NULL, state_version INTEGER NOT NULL DEFAULT 0, created_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS observations(obs_id TEXT PRIMARY KEY,twin_id TEXT NOT NULL REFERENCES twins(twin_id) ON DELETE CASCADE,obs_type TEXT NOT NULL,value REAL NOT NULL,unit TEXT NOT NULL,observed_at TEXT NOT NULL,source_id TEXT NOT NULL,provenance TEXT NOT NULL, UNIQUE(twin_id,obs_type,observed_at,source_id));
        CREATE TABLE IF NOT EXISTS predictions(prediction_id TEXT PRIMARY KEY,twin_id TEXT NOT NULL REFERENCES twins(twin_id) ON DELETE CASCADE,as_of TEXT NOT NULL,state_version INTEGER NOT NULL,risk_probability REAL NOT NULL,risk_band TEXT NOT NULL,model_version TEXT NOT NULL,features_json TEXT NOT NULL,created_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS ingest_audit(id INTEGER PRIMARY KEY AUTOINCREMENT,twin_id TEXT,kind TEXT,reason TEXT,payload_json TEXT,created_at TEXT);
        ''')
''
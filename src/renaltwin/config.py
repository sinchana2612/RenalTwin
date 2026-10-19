from pathlib import Path
import os, yaml
ROOT=Path(__file__).resolve().parents[2]
def load_yaml(name):
    path=ROOT/"configs"/name
    with path.open() as f: return yaml.safe_load(f)
def get_paths():
    return {"data":Path(os.getenv("RT_DATA_DIR", ROOT/"data")), "artifacts":Path(os.getenv("RT_ARTIFACT_DIR", ROOT/"artifacts")), "db_url":os.getenv("RT_DB_URL", f"sqlite:///{ROOT/'artifacts'/'renaltwin.db'}")}

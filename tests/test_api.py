from fastapi.testclient import TestClient
from renaltwin.api.main import app
from renaltwin.db.store import init_db
def test_health():
 init_db(); c=TestClient(app); r=c.get("/api/v1/health"); assert r.status_code==200 and r.json()["status"]=="ok"
def test_create_twin():
 c=TestClient(app); r=c.post("/api/v1/twins",json={"display_name":"Test twin","age_at_enrollment":60,"sex":"F","diabetes":True,"hypertension":True,"data_origin":"synthetic"}); assert r.status_code==201 and r.json()["twin_id"].startswith("tw_")


def test_twin_ingest_state_and_prediction():
 from renaltwin.twin.engine import TwinEngine
 from renaltwin.ml.predictor import Predictor
 from pathlib import Path
 init_db()
 predictor=Predictor.load(Path("artifacts/models/v1"))
 e=TwinEngine(predictor)
 t=e.create({"display_name":"Feature twin","age_at_enrollment":60,"sex":"F","diabetes":True,"hypertension":True,"data_origin":"synthetic"})
 tid=t["twin_id"]
 result=e.ingest(tid,[{"obs_type":"egfr","value":70,"unit":"mL/min/1.73 m2","observed_at":"2025-01-01T00:00:00Z","source_id":"a"},{"obs_type":"egfr","value":64,"unit":"mL/min/1.73 m2","observed_at":"2025-04-01T00:00:00Z","source_id":"b"}],"clinical")
 assert result["accepted"]==2 and result["twin_status"]=="ready"
 state=e.state(tid); assert state["features"] and state["features"]["egfr_last"]["value"]==64
 pred=e.predict(tid); assert 0 <= pred["risk_probability"] <= 1

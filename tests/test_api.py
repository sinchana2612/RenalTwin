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
 assert pred["horizon_days"]==365 and pred["features"]["egfr_last"]==64.0


def test_clinical_features_and_predictions_follow_observation_history():
 from renaltwin.twin.engine import TwinEngine
 from renaltwin.ml.predictor import Predictor
 from renaltwin.constants import FEATURE_NAMES
 from pathlib import Path
 init_db()
 e=TwinEngine(Predictor.load(Path("artifacts/models/v1")))
 common=[
  {"obs_type":"uacr","value":145,"unit":"mg/g","observed_at":"2025-01-01T00:00:00Z"},
  {"obs_type":"hba1c","value":7.1,"unit":"%","observed_at":"2025-01-01T00:00:00Z"},
  {"obs_type":"hemoglobin","value":12.8,"unit":"g/dL","observed_at":"2025-01-01T00:00:00Z"},
  {"obs_type":"potassium","value":4.5,"unit":"mmol/L","observed_at":"2025-01-01T00:00:00Z"},
  {"obs_type":"sbp_clinic","value":138,"unit":"mmHg","observed_at":"2025-01-01T00:00:00Z"},
 ]
 histories=[]
 for label, values in (("A",(72,58)),("B",(110,105))):
  t=e.create({"display_name":"History "+label,"age_at_enrollment":60,"sex":"F","diabetes":True,"hypertension":True,"data_origin":"synthetic"})
  obs=[{"obs_type":"egfr","value":v,"unit":"mL/min/1.73 m2","observed_at":d,"source_id":label+d} for v,d in zip(values,("2025-01-01T00:00:00Z","2025-04-01T00:00:00Z"))]
  obs += [{**x,"source_id":label+x["obs_type"]} for x in common]
  assert e.ingest(t["twin_id"],obs)["twin_status"]=="ready"
  state=e.state(t["twin_id"])
  assert list(state["features"])==FEATURE_NAMES
  assert all(isinstance(x["value"],float) for x in state["features"].values())
  histories.append((t["twin_id"],state))
 assert histories[0][1]["features"]["egfr_last"]["value"] != histories[1][1]["features"]["egfr_last"]["value"]
 results=[e.predict(tid) for tid,_ in histories]
 predictions=[x["risk_probability"] for x in results]
 assert all(x["horizon_days"]==365 for x in results)
 assert predictions[0] != predictions[1]


def test_demo_2_observations_are_prediction_ready():
 from renaltwin.twin.engine import TwinEngine
 from renaltwin.ml.predictor import Predictor
 from pathlib import Path
 init_db()
 e=TwinEngine(Predictor.load(Path("artifacts/models/v1")))
 t=e.create({"display_name":"Demo 2","age_at_enrollment":60,"sex":"F","diabetes":True,"hypertension":True,"data_origin":"synthetic"})
 tid=t["twin_id"]
 values=[("egfr",72,"mL/min/1.73 m2","2025-01-01"),("egfr",58,"mL/min/1.73 m2","2025-04-01"),("uacr",145,"mg/g","2025-04-01"),("hba1c",7.1,"%","2025-04-01"),("hemoglobin",12.8,"g/dL","2025-04-01"),("potassium",4.5,"mmol/L","2025-04-01"),("sbp_clinic",138,"mmHg","2025-04-01")]
 observations=[{"obs_type":typ,"value":value,"unit":unit,"observed_at":date+"T00:00:00Z","source_id":str(i)} for i,(typ,value,unit,date) in enumerate(values)]
 assert e.ingest(tid,observations)["twin_status"]=="ready"
 assert e.state(tid)["features"]["egfr_last"]["value"]==58.0
 prediction=e.predict(tid)
 assert prediction["status"]=="ok" and prediction["horizon_days"]==365
 assert prediction["features"]["egfr_last"]==58.0


def test_fractional_and_whole_second_timestamps_are_accepted():
 from fastapi.testclient import TestClient
 from renaltwin.api.main import app
 from renaltwin.db.store import init_db
 init_db()
 client=TestClient(app)
 twin=client.post("/api/v1/twins",json={"display_name":"Timestamp twin","age_at_enrollment":60,"sex":"F","diabetes":False,"hypertension":False}).json()
 tid=twin["twin_id"]
 payload=[
  {"obs_type":"egfr","value":70,"unit":"mL/min/1.73 m2","observed_at":"2026-10-18T18:30:00+00:00","source_id":"whole"},
  {"obs_type":"egfr","value":68,"unit":"mL/min/1.73 m2","observed_at":"2026-10-18T18:30:00.123456+00:00","source_id":"fractional"},
 ]
 response=client.post(f"/api/v1/twins/{tid}/clinical-observations",json=payload)
 assert response.status_code==200 and response.json()["accepted"]==2
 state=client.get(f"/api/v1/twins/{tid}/state").json()
 assert state["last_egfr_at"].endswith(".123456+00:00")
 assert state["counts"]["egfr_365d"]==2

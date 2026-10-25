import os, json, uuid
from pathlib import Path
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException, Header, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator
from renaltwin.db.store import init_db, connect
from renaltwin.twin.engine import TwinEngine
from renaltwin.ml.predictor import Predictor
from renaltwin.constants import DISCLAIMER
from renaltwin.config import get_paths

class TwinCreate(BaseModel):
 display_name:str=Field(min_length=1,max_length=60); age_at_enrollment:int=Field(ge=18,le=110); sex:str; diabetes:bool; hypertension:bool; cvd:bool=False; data_origin:str="synthetic"
 @field_validator("sex")
 @classmethod
 def sex_ok(cls,v):
  if v not in {"F","M","U"}: raise ValueError("sex must be F, M or U")
  return v
class Observation(BaseModel):
 obs_type:str; value:float; unit:str; observed_at:datetime; source_id:str="manual"; provenance:str="manual"
 @field_validator("observed_at")
 @classmethod
 def utc(cls,v): return v.replace(tzinfo=timezone.utc) if v.tzinfo is None else v.astimezone(timezone.utc)
app=FastAPI(title="RenalTwin API",version="0.1.0",description=DISCLAIMER)
engine=TwinEngine()
def get_engine():
 paths=get_paths(); active=paths["artifacts"]/"models"/"v1"
 try: predictor=Predictor.load(active) if (active/"b1.joblib").exists() else None
 except Exception: predictor=None
 return TwinEngine(predictor)
@app.on_event("startup")
def startup(): init_db(); global engine; engine=get_engine()
@app.middleware("http")
async def auth(request,call_next):
 key=os.getenv("RT_API_KEY","")
 if key and request.url.path!="/api/v1/health" and request.headers.get("X-API-Key")!=key: return JSONResponse(status_code=401,content={"error":{"code":"unauthorized","message":"Invalid or missing API key","details":[]},"request_id":uuid.uuid4().hex})
 return await call_next(request)
def error(code,msg,status,details=None): return JSONResponse(status_code=status,content={"error":{"code":code,"message":msg,"details":details or []},"request_id":"req_"+uuid.uuid4().hex[:8]})
@app.get("/api/v1/health")
def health(): return {"status":"ok","time":datetime.now(timezone.utc).isoformat(),"disclaimer":DISCLAIMER}
@app.get("/api/v1/model/status")
def model_status():
 if not engine.predictor:return error("model_unavailable","Train a model using `renaltwin train` first.",503)
 return {"version":engine.predictor.manifest["version"],"feature_set":"clinical","metrics":engine.predictor.metrics,"disclaimer":DISCLAIMER}
@app.get("/api/v1/data/status")
def data_status():return {"default_data":"synthetic","real_data_optional":["UCI CKD cross-sectional","MIMIC-IV demo ICU replay"],"patient_level_linkage":False,"disclaimer":DISCLAIMER}
@app.post("/api/v1/twins",status_code=201)
def create_twin(body:TwinCreate):
 try:return engine.create(body.model_dump())
 except Exception as e:return error("validation_error",str(e),422)
@app.get("/api/v1/twins")
def list_twins(limit:int=Query(50,ge=1,le=100),offset:int=Query(0,ge=0)):return engine.list()[offset:offset+limit]
@app.get("/api/v1/twins/{tid}")
def get_twin(tid):
 try:return engine.get(tid)
 except KeyError:return error("not_found","Twin not found",404)
@app.post("/api/v1/twins/{tid}/clinical-observations")
def clinical(tid,body:list[Observation]):
 try:return engine.ingest(tid,[x.model_dump(mode="json") for x in body],"clinical")
 except KeyError:return error("not_found","Twin not found",404)
@app.post("/api/v1/twins/{tid}/sensor-observations")
def sensors(tid,body:list[Observation]):
 try:return engine.ingest(tid,[x.model_dump(mode="json") for x in body],"sensor")
 except KeyError:return error("not_found","Twin not found",404)
@app.get("/api/v1/twins/{tid}/observations")
def observations(tid,type:str|None=None):
 try:return engine.observations(tid,type)
 except KeyError:return error("not_found","Twin not found",404)
@app.get("/api/v1/twins/{tid}/state")
def state(tid,as_of:str|None=None):
 try:return engine.state(tid,as_of)
 except KeyError:return error("not_found","Twin not found",404)
 except RuntimeError as e:return error("feature_extraction_failed",str(e),500)
@app.post("/api/v1/twins/{tid}/predict")
def predict(tid,as_of:str|None=None):
 try:return engine.predict(tid,as_of)
 except KeyError:return error("not_found","Twin not found",404)
 except RuntimeError as e:
  if str(e).startswith("clinical_feature_extraction_failed"):
   return error("feature_extraction_failed",str(e),500)
  return error("model_unavailable",str(e),503)
 except ValueError as e:return error("not_ready",str(e),409)
@app.get("/api/v1/twins/{tid}/risk-history")
def risk_history(tid):
 try:return engine.risk_history(tid)
 except KeyError:return error("not_found","Twin not found",404)
@app.post("/api/v1/twins/{tid}/reset")
def reset(tid):
 try:return engine.reset(tid)
 except KeyError:return error("not_found","Twin not found",404)
@app.delete("/api/v1/twins/{tid}",status_code=204)
def delete_twin(tid):
 try:engine.get(tid)
 except KeyError: raise HTTPException(404,"Twin not found")
 with connect() as c:c.execute("DELETE FROM twins WHERE twin_id=?",(tid,))
 return None
@app.get("/api/v1/twins/{tid}/explanations/{prediction_id}")
def explanation(tid,prediction_id):
 try: rows=engine.risk_history(tid)
 except KeyError:return error("not_found","Twin not found",404)
 for r in rows:
  if r["prediction_id"]==prediction_id:return {"prediction_id":prediction_id,"contributors":[],"note":"Logistic baseline currently exposes model-level coefficients; per-row contribution display is not enabled in this build."}
 return error("not_found","Prediction not found",404)

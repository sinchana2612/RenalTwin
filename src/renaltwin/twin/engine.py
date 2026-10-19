import uuid, json, math
from datetime import datetime, timezone, timedelta
import numpy as np, pandas as pd
from renaltwin.db.store import connect
from renaltwin.data.build_dataset import features_at
from renaltwin.constants import DISCLAIMER
from renaltwin.ml.predictor import Predictor
from renaltwin.units import convert, UnitError
ALLOWED={"creatinine","egfr","uacr","hba1c","potassium","hemoglobin","sbp_clinic","hr_rest","sbp_home","sleep_min","steps"}
RANGES={"creatinine":(.2,20),"egfr":(1,200),"uacr":(0,50000),"hba1c":(3,25),"potassium":(1.5,10),"hemoglobin":(2,25),"sbp_clinic":(50,300),"hr_rest":(25,220),"sbp_home":(50,300),"sleep_min":(0,1440),"steps":(0,100000)}
def now(): return datetime.now(timezone.utc).isoformat()
def make_id(prefix): return prefix+uuid.uuid4().hex[:12]
class TwinEngine:
    def __init__(self,predictor=None): self.predictor=predictor
    def create(self,data):
        tid=make_id("tw_");
        with connect() as c: c.execute("INSERT INTO twins VALUES(?,?,?,?,?,?,?,?,?,?)",(tid,data["display_name"],data["age_at_enrollment"],data["sex"],int(data["diabetes"]),int(data["hypertension"]),int(data.get("cvd",False)),data.get("data_origin","synthetic"),0,now()))
        return self.get(tid)
    def get(self,tid):
        with connect() as c: r=c.execute("SELECT * FROM twins WHERE twin_id=?",(tid,)).fetchone()
        if not r: raise KeyError(tid)
        return dict(r)
    def list(self):
        with connect() as c: return [dict(r) for r in c.execute("SELECT * FROM twins ORDER BY created_at DESC").fetchall()]
    def ingest(self,tid,items,kind="clinical"):
        if not self._exists(tid): raise KeyError(tid)
        accepted=duplicates=conflicts=0; rejected=[]; out_of_order=False
        with connect() as c:
            before=c.execute("SELECT MAX(observed_at) m FROM observations WHERE twin_id=?",(tid,)).fetchone()["m"]
            for i,x in enumerate(items):
                try:
                    typ=x["obs_type"]; val=float(x["value"]); unit=x["unit"]; ts=pd.Timestamp(x["observed_at"])
                    if typ not in ALLOWED or (kind=="sensor" and typ not in {"hr_rest","sbp_home","sleep_min","steps"}) or (kind=="clinical" and typ in {"hr_rest","sbp_home","sleep_min","steps"}): raise ValueError("unknown_or_wrong_observation_type")
                    val,unit=convert(typ,val,unit); lo,hi=RANGES[typ]
                    if not math.isfinite(val) or not lo<=val<=hi: raise ValueError("out_of_range")
                    if ts.year<1990: raise ValueError("timestamp_before_1990")
                    ts=ts.tz_convert("UTC") if ts.tzinfo else ts.tz_localize("UTC"); iso=ts.isoformat(); src=x.get("source_id","manual"); prov=x.get("provenance","manual")
                    if before and iso<before: out_of_order=True
                    old=c.execute("SELECT value FROM observations WHERE twin_id=? AND obs_type=? AND observed_at=? AND source_id=?",(tid,typ,iso,src)).fetchone()
                    if old:
                        if abs(old["value"]-val)<1e-9: duplicates+=1
                        else:
                            conflicts+=1;c.execute("INSERT INTO ingest_audit(twin_id,kind,reason,payload_json,created_at) VALUES(?,?,?,?,?)",(tid,kind,"conflict",json.dumps(x),now()))
                        continue
                    c.execute("INSERT INTO observations VALUES(?,?,?,?,?,?,?,?)",(make_id("ob_"),tid,typ,val,unit,iso,src,prov));accepted+=1
                except Exception as e:
                    rejected.append({"index":i,"reason":str(e)});c.execute("INSERT INTO ingest_audit(twin_id,kind,reason,payload_json,created_at) VALUES(?,?,?,?,?)",(tid,kind,str(e),json.dumps(x,default=str),now()))
            if accepted: c.execute("UPDATE twins SET state_version=state_version+1 WHERE twin_id=?",(tid,))
            ver=c.execute("SELECT state_version FROM twins WHERE twin_id=?",(tid,)).fetchone()[0]
        return {"accepted":accepted,"duplicates":duplicates,"conflicts":conflicts,"rejected":rejected,"out_of_order":out_of_order,"state_version":ver,"twin_status":self.state(tid)["status"]}
    def _exists(self,tid):
        with connect() as c:return c.execute("SELECT 1 FROM twins WHERE twin_id=?",(tid,)).fetchone() is not None
    def view(self,tid):
        profile=self.get(tid)
        with connect() as c: rows=[dict(r) for r in c.execute("SELECT * FROM observations WHERE twin_id=? ORDER BY observed_at",(tid,)).fetchall()]
        labs=pd.DataFrame(rows);
        if labs.empty: labs=pd.DataFrame(columns=["obs_type","value","observed_at"])
        labs["dt"]=pd.to_datetime(labs.observed_at,utc=True,errors="coerce") if len(labs) else pd.to_datetime([] ,utc=True)
        return profile,labs
    def state(self,tid,as_of=None):
        profile,labs=self.view(tid); asof=pd.Timestamp(as_of) if as_of else (labs.dt.max() if len(labs) else pd.Timestamp.now(tz="UTC"));
        if asof.tzinfo is None: asof=asof.tz_localize("UTC")
        labs=labs[labs.dt<=asof] if len(labs) else labs
        eg=labs[labs.obs_type=="egfr"] if len(labs) else labs; n=len(eg); span=(eg.dt.max()-eg.dt.min()).days if n>=2 else 0; age=(asof-pd.Timestamp(profile["created_at"])).days
        status="created" if not len(labs) else "static_only" if n<2 else "insufficient_history" if span<60 else "ready"
        if n and (asof-eg.dt.max()).days>365: status="stale"
        features={};
        if len(labs):
            obj=type("P",(),{"age":profile["age"],"sex":profile["sex"],"diabetes":profile["diabetes"],"hypertension":profile["hypertension"],"cvd":profile["cvd"]})()
            # convert stored observation shape into the feature builder's expected shape
            fdf=labs[["obs_type","value","observed_at"]].copy(); fdf["observed_at"]=fdf.observed_at.astype(str)
            try: features=__import__("renaltwin.data.build_dataset",fromlist=["features_at"]).features_at(obj,fdf,asof)
            except Exception: features={}
        from renaltwin.egfr import ckd_stage
        latest=float(eg.sort_values("dt").iloc[-1].value) if n else None
        return {"twin_id":tid,"state_version":profile["state_version"],"as_of":asof.isoformat(),"status":status,"ckd_stage":ckd_stage(latest),"features":{k:{"value":(None if pd.isna(v) else float(v)),"value_origin":"derived","missing":bool(pd.isna(v))} for k,v in features.items()},"quality_flags":["synthetic_data" if profile["data_origin"]=="synthetic" else "deidentified_data"],"counts":{"egfr_365d":int(((eg.dt>=asof-pd.Timedelta(days=365))&(eg.dt<=asof)).sum()) if n else 0},"last_egfr_at":eg.dt.max().isoformat() if n else None,"disclaimer":DISCLAIMER}
    def observations(self,tid,typ=None):
        if not self._exists(tid): raise KeyError(tid)
        with connect() as c:
            q="SELECT * FROM observations WHERE twin_id=?";args=[tid]
            if typ:q+=" AND obs_type=?";args.append(typ)
            q+=" ORDER BY observed_at";return [dict(r) for r in c.execute(q,args).fetchall()]
    def predict(self,tid,as_of=None):
        if not self.predictor: raise RuntimeError("model_unavailable: train model first")
        state=self.state(tid,as_of);
        if state["status"] not in {"ready","stale"}: raise ValueError("not_ready:"+state["status"])
        if state["status"]=="stale": raise ValueError("not_ready:stale")
        feats={k:v["value"] for k,v in state["features"].items()}; result=self.predictor.predict(feats); pid=make_id("pr_");
        with connect() as c:
            c.execute("INSERT INTO predictions VALUES(?,?,?,?,?,?,?,?,?)",(pid,tid,state["as_of"],state["state_version"],result["risk_probability"],result["risk_band"],result["model_version"],json.dumps(feats),now()))
        return {"prediction_id":pid,"twin_id":tid,"as_of":state["as_of"],"state_version":state["state_version"],"status":"ok","reason":None,"horizon_days":365,**result,"top_contributors":[],"quality_flags":state["quality_flags"]}
    def risk_history(self,tid):
        if not self._exists(tid): raise KeyError(tid)
        with connect() as c:return [dict(r) for r in c.execute("SELECT * FROM predictions WHERE twin_id=? ORDER BY as_of",(tid,)).fetchall()]
    def reset(self,tid):
        if not self._exists(tid):raise KeyError(tid)
        with connect() as c:c.execute("DELETE FROM observations WHERE twin_id=?",(tid,));c.execute("DELETE FROM predictions WHERE twin_id=?",(tid,));c.execute("UPDATE twins SET state_version=state_version+1 WHERE twin_id=?",(tid,))
        return {"reset":True,"twin_id":tid}

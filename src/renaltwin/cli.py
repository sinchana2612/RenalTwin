import argparse, json
from pathlib import Path
from renaltwin.config import get_paths
from renaltwin.data.synthetic_cohort import generate_cohort
from renaltwin.data.build_dataset import build_training_table
from renaltwin.ml.train import train
from renaltwin.db.store import init_db
from renaltwin.twin.engine import TwinEngine

def main():
 p=argparse.ArgumentParser(prog="renaltwin"); sub=p.add_subparsers(dest="cmd",required=True)
 data=sub.add_parser("data"); ds=data.add_subparsers(dest="data_cmd",required=True); syn=ds.add_parser("synth");syn.add_argument("--n-patients",type=int,default=3000);syn.add_argument("--seed",type=int,default=42);syn.add_argument("--sensor-coupling",type=float,default=0.0); build=ds.add_parser("build");build.add_argument("--feature-set",default="clinical")
 tr=sub.add_parser("train");tr.add_argument("--seed",type=int,default=42)
 sub.add_parser("evaluate"); db=sub.add_parser("db");db.add_subparsers(dest="db_cmd",required=True).add_parser("init"); demo=sub.add_parser("demo");demo.add_subparsers(dest="demo_cmd",required=True).add_parser("seed");sub.add_parser("status")
 a=p.parse_args(); paths=get_paths(); data_dir=paths["data"]; art=paths["artifacts"]
 if a.cmd=="data" and a.data_cmd=="synth":
  c=generate_cohort(a.n_patients,a.seed,data_dir/"synthetic",a.sensor_coupling);print(json.dumps({"patients":len(c["patients"]),"labs":len(c["labs"]),"labels":len(c["labels"]),"path":str(data_dir/"synthetic")},indent=2))
 elif a.cmd=="data" and a.data_cmd=="build":
  import pandas as pd
  d=data_dir/"synthetic"; c={n:pd.read_csv(d/f"{n}.csv") for n in ["patients","labs","sensor_daily","labels","hidden_truth"]}; df=build_training_table(c,data_dir/"processed");print(json.dumps({"landmarks":len(df),"prevalence":float(df.label.mean()) if len(df) else None,"output":str(data_dir/"processed/landmarks.csv")},indent=2))
 elif a.cmd=="train":
  import pandas as pd
  df=pd.read_csv(data_dir/"processed/landmarks.csv"); model,metrics=train(df,art/"models/v1",a.seed);print(json.dumps(metrics,indent=2))
 elif a.cmd=="evaluate":
  f=art/"models/v1/metrics.json";print(f.read_text() if f.exists() else "No metrics yet; run data synth, data build, train.")
 elif a.cmd=="db":init_db();print("Database initialized")
 elif a.cmd=="demo":
  from datetime import datetime, timezone, timedelta
  init_db(); e=TwinEngine(); t=e.create({"display_name":"Synthetic replay patient","age_at_enrollment":62,"sex":"F","diabetes":True,"hypertension":True,"cvd":False,"data_origin":"synthetic"}); tid=t["twin_id"]; now=datetime.now(timezone.utc)
  obs=[]
  for days,val in [(180,76.0),(120,73.0),(60,69.0),(0,65.0)]:
   ts=(now-timedelta(days=days)).isoformat(); obs.append({"obs_type":"egfr","value":val,"unit":"mL/min/1.73 m2","observed_at":ts,"source_id":f"demo-egfr-{days}","provenance":"synthetic"}); obs.append({"obs_type":"uacr","value":95+days/10,"unit":"mg/g","observed_at":ts,"source_id":f"demo-uacr-{days}","provenance":"synthetic"}); obs.append({"obs_type":"hba1c","value":7.1,"unit":"%","observed_at":ts,"source_id":f"demo-a1c-{days}","provenance":"synthetic"})
  result=e.ingest(tid,obs,"clinical"); print(json.dumps({"created_twin":t,"ingestion":result,"state":e.state(tid),"next":"Open the dashboard or POST /api/v1/twins/{id}/predict"},indent=2))
 elif a.cmd=="status":print(json.dumps({"data_exists":(data_dir/"synthetic/patients.csv").exists(),"model_exists":(art/"models/v1/b1.joblib").exists(),"db_exists":(art/"renaltwin.db").exists()},indent=2))
if __name__=="__main__":main()

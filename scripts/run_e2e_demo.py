"""Exercise the public API against a running RenalTwin server."""
import os, sys
import requests
BASE=os.getenv("RT_API_URL","http://127.0.0.1:8000").rstrip("/")+"/api/v1"
def main():
    r=requests.get(BASE+"/health",timeout=5); r.raise_for_status()
    payload={"display_name":"E2E synthetic twin","age_at_enrollment":62,"sex":"F","diabetes":True,"hypertension":True,"cvd":False,"data_origin":"synthetic"}
    t=requests.post(BASE+"/twins",json=payload,timeout=10); t.raise_for_status(); twin=t.json(); tid=twin["twin_id"]
    from datetime import datetime,timezone,timedelta
    now=datetime.now(timezone.utc); obs=[]
    for days,value in [(180,78),(120,74),(60,69),(0,64)]:
        obs.append({"obs_type":"egfr","value":value,"unit":"mL/min/1.73 m2","observed_at":(now-timedelta(days=days)).isoformat(),"source_id":f"e2e-{days}","provenance":"synthetic"})
    ing=requests.post(f"{BASE}/twins/{tid}/clinical-observations",json=obs,timeout=10); ing.raise_for_status()
    state=requests.get(f"{BASE}/twins/{tid}/state",timeout=10); state.raise_for_status()
    pred=requests.post(f"{BASE}/twins/{tid}/predict",timeout=10)
    if pred.status_code!=200: raise RuntimeError(f"prediction failed: {pred.status_code} {pred.text}")
    result=pred.json()
    print(f"PASS twin={tid} accepted={ing.json()['accepted']} status={state.json()['status']} risk={result['risk_probability']:.4f} model={result['model_version']}")
if __name__=="__main__": main()

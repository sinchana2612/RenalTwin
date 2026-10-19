import numpy as np, pandas as pd
def clinical_features(profile, observations, as_of):
    t=pd.Timestamp(as_of); t=t.tz_localize("UTC") if t.tzinfo is None else t.tz_convert("UTC")
    df=observations.copy()
    if not df.empty:
        df["observed_at"]=pd.to_datetime(df.observed_at,utc=True); df=df[df.observed_at<=t].sort_values("observed_at")
    eg=df[df.obs_type=="egfr"] if not df.empty else pd.DataFrame()
    recent=eg[eg.observed_at>=t-pd.Timedelta(days=365)] if not eg.empty else eg
    vals=recent.value.astype(float).to_numpy() if not recent.empty else np.array([])
    slope=float("nan")
    if len(vals)>=2 and (recent.observed_at.max()-recent.observed_at.min()).days>=60:
        x=(recent.observed_at-recent.observed_at.min()).dt.total_seconds().to_numpy()/86400/365; slope=float(np.polyfit(x,vals,1)[0])
    def last(kind):
        z=df[df.obs_type==kind] if not df.empty else pd.DataFrame(); return float(z.iloc[-1].value) if not z.empty else float("nan")
    last_egfr=last("egfr"); last_at=eg.observed_at.max() if not eg.empty else None
    return {"age":float(profile.get("age",60)),"diabetes":float(bool(profile.get("diabetes",False))),"hypertension":float(bool(profile.get("hypertension",False))),"egfr_last":last_egfr,"egfr_slope_per_year":slope,"egfr_sd":float(np.std(vals)) if len(vals)>1 else float("nan"),"uacr_last":last("uacr"),"hba1c_last":last("hba1c"),"systolic_bp_last":last("sbp_clinic"),"days_since_last_egfr":float((t-last_at).total_seconds()/86400) if last_at is not None else float("nan"),"n_egfr_365d":int(len(vals))}

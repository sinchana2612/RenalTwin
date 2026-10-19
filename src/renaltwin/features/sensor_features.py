import pandas as pd
def sensor_features(observations, as_of):
    t=pd.Timestamp(as_of); t=t.tz_localize("UTC") if t.tzinfo is None else t.tz_convert("UTC"); d=observations.copy()
    if not d.empty: d["observed_at"]=pd.to_datetime(d.observed_at,utc=True); d=d[(d.observed_at<=t)&(d.observed_at>=t-pd.Timedelta(days=28))]
    def mean(kind,days):
        x=d[(d.obs_type==kind)&(d.observed_at>=t-pd.Timedelta(days=days))] if not d.empty else d
        return float(x.value.mean()) if not x.empty else float("nan")
    return {"hr_rest_mean_7d":mean("hr_rest",7),"sbp_home_mean_7d":mean("sbp_home",7),"sleep_min_mean_7d":mean("sleep_min",7),"steps_mean_7d":mean("steps",7),"sensor_coverage_28d":float(d.observed_at.dt.date.nunique()/28) if not d.empty else 0.0}

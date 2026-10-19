from pathlib import Path
import json
import numpy as np
from joblib import load
from renaltwin.constants import FEATURE_NAMES
class Predictor:
    def __init__(self,model,manifest,metrics): self.model=model; self.manifest=manifest; self.metrics=metrics
    @classmethod
    def load(cls,artifact_dir="artifacts/models/v1"):
        p=Path(artifact_dir); return cls(load(p/"b1.joblib"),json.loads((p/"manifest.json").read_text()),json.loads((p/"metrics.json").read_text()))
    def predict(self,features):
        if self.manifest["feature_names"]!=FEATURE_NAMES: raise RuntimeError("model feature schema incompatible")
        import pandas as pd
        x=pd.DataFrame([[features.get(k,np.nan) for k in FEATURE_NAMES]],columns=FEATURE_NAMES); prob=float(self.model.predict_proba(x)[0,1]); return {"risk_probability":prob,"risk_band":"high" if prob>=.65 else "moderate" if prob>=.35 else "low","model_version":self.manifest["version"],"feature_set":"clinical","disclaimer":"Research prototype only. Not medical advice."}

from pathlib import Path
import json, hashlib
import numpy as np, pandas as pd
from sklearn.model_selection import GroupShuffleSplit
from sklearn.impute import SimpleImputer
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.metrics import roc_auc_score, average_precision_score, brier_score_loss, accuracy_score
from joblib import dump
from renaltwin.constants import FEATURE_NAMES

def train(df, artifact_dir="artifacts/models/v1", seed=42):
    out=Path(artifact_dir);out.mkdir(parents=True,exist_ok=True)
    if len(df)<100: raise ValueError(f"Need at least 100 labelled landmarks; got {len(df)}")
    X=df[FEATURE_NAMES].replace([np.inf,-np.inf],np.nan); y=df.label.astype(int); groups=df.patient_id.astype(str)
    # Deterministic patient-level split.
    unique=np.array(sorted(groups.unique())); rng=np.random.default_rng(seed); rng.shuffle(unique); n=len(unique); tr=set(unique[:int(.70*n)]); va=set(unique[int(.70*n):int(.85*n)]); te=set(unique[int(.85*n):]);
    if tr&va or tr&te or va&te: raise AssertionError("patient split overlap")
    idxtr=groups.isin(tr); idxva=groups.isin(va); idxte=groups.isin(te)
    if y[idxtr].nunique()<2: raise ValueError("training split has only one class; increase cohort size")
    model=make_pipeline(SimpleImputer(strategy="median",add_indicator=True),StandardScaler(),LogisticRegression(max_iter=2000,class_weight="balanced",random_state=seed))
    model.fit(X[idxtr],y[idxtr]); pred=model.predict_proba(X[idxte])[:,1];
    metrics={"n_rows":int(len(df)),"n_patients":int(groups.nunique()),"prevalence":float(y.mean()),"test_n":int(idxte.sum()),"test_prevalence":float(y[idxte].mean()),"test_auroc":float(roc_auc_score(y[idxte],pred)) if y[idxte].nunique()>1 else None,"test_auprc":float(average_precision_score(y[idxte],pred)),"test_brier":float(brier_score_loss(y[idxte],pred)),"test_accuracy_at_0_5":float(accuracy_score(y[idxte],pred>=.5)),"warning":"Synthetic simulator evaluation only; not clinical evidence."}
    dump(model,out/"b1.joblib"); (out/"metrics.json").write_text(json.dumps(metrics,indent=2)); (out/"manifest.json").write_text(json.dumps({"version":"v1","feature_names":FEATURE_NAMES,"seed":seed,"model":"LogisticRegression","data_hash":hashlib.sha256(pd.util.hash_pandas_object(df,index=True).values.tobytes()).hexdigest(),"synthetic_only":True},indent=2)); (out/"ACTIVE").write_text("v1")
    return model,metrics

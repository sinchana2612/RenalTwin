import numpy as np
from renaltwin.egfr import ckd_epi_2021, creatinine_from_egfr, ckd_stage
from renaltwin.units import convert, UnitError
from renaltwin.data.synthetic_cohort import generate_cohort
from renaltwin.data.build_dataset import build_training_table

def test_egfr_round_trip():
 for sex in ["F","M"]:
  scr=creatinine_from_egfr(60,55,sex); assert abs(ckd_epi_2021(scr,55,sex)-60)<1e-3
def test_units():
 v,u=convert("creatinine",88.4,"umol/L"); assert abs(v-1)<1e-8 and u=="mg/dL"
 try: convert("creatinine",1,"stone")
 except UnitError: pass
 else: assert False
def test_stage(): assert ckd_stage(95)=="G1" and ckd_stage(12)=="G5"
def test_synth_deterministic():
 a=generate_cohort(40,7); b=generate_cohort(40,7); assert a["patients"].equals(b["patients"]); assert len(a["labs"])>0
def test_feature_builder_no_future_data():
 c=generate_cohort(20,9); df=build_training_table(c); assert len(df)>0; assert "latent_class" not in df.columns and "true_slope" not in df.columns

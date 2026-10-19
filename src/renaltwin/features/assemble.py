from renaltwin.features.clinical_features import clinical_features
from renaltwin.features.sensor_features import sensor_features
FEATURES={"clinical":["age","diabetes","hypertension","egfr_last","egfr_slope_per_year","egfr_sd","uacr_last","hba1c_last","systolic_bp_last","days_since_last_egfr"],"clinical_sensor":["age","diabetes","hypertension","egfr_last","egfr_slope_per_year","egfr_sd","uacr_last","hba1c_last","systolic_bp_last","days_since_last_egfr","hr_rest_mean_7d","sbp_home_mean_7d","sleep_min_mean_7d","steps_mean_7d"]}
def build_feature_vector(profile, clinical, sensors, as_of, feature_set="clinical"):
    f=clinical_features(profile,clinical,as_of); f.update(sensor_features(sensors,as_of)); names=FEATURES[feature_set]
    result={k:f.get(k,float("nan")) for k in names}; result["n_egfr_365d"]=f.get("n_egfr_365d",0); return result, ["low_egfr_count"] if f.get("n_egfr_365d",0)<2 else []

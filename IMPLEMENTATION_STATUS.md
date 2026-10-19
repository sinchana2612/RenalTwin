# Implementation status (honest handoff)

## Implemented and exercised
- Deterministic synthetic cohort generation and CSV export.
- Landmark feature construction with as-of truncation and hidden simulator truth excluded from model features.
- Patient-level train/test split and logistic-regression training pipeline; generated model artifact, manifest, and actual test metrics.
- CKD-EPI 2021 equation utility, creatinine inverse utility, CKD stage categorization, and unit conversion.
- SQLite persistence for twins, observations, predictions, and ingest audit.
- FastAPI health/model/data endpoints; twin CRUD, clinical/sensor ingestion, observation/state retrieval, prediction, risk history, explanation placeholder, reset and delete.
- Input range/type checks, idempotent duplicates, conflict audit, state versioning, data provenance and medical disclaimer.
- Streamlit dashboard source backed by the API, including twin creation, eGFR chart, observation entry, prediction and risk history.
- Tests for eGFR/unit utilities, deterministic synthesis, feature construction, API health/create, ingestion/state/prediction.
- Real HTTP end-to-end smoke run succeeded against Uvicorn.

## Deliberately not represented as complete
- The full 18-endpoint contract in the blueprint: scenario and replay/outcome endpoints are not implemented in this build.
- Optional UCI and MIMIC-IV download/ingestion adapters are documented but not implemented.
- The advanced LightGBM model, hyperparameter search, probability calibration, clustered bootstrap confidence intervals, subgroup analysis, drift monitoring, and per-row SHAP explanations are not implemented; the current active model is a logistic-regression baseline.
- The model is trained only on synthetic data. Its metrics are not clinical evidence. The synthetic outcome generator is simplified and is not a clinical endpoint implementation.
- The dashboard is a working single-page app, not the full six-page dashboard specified in the blueprint. Docker files are supplied but were not tested in this environment.
- The optional Streamlit UI could not be launched in the build environment because Streamlit was not installed; it is declared as an install extra.

## Verification results in this environment
- `PYTHONPATH=src pytest -q`: 8 passed, 2 FastAPI deprecation warnings.
- A live Uvicorn HTTP smoke test created a twin, ingested four eGFR measurements, retrieved state, and returned a prediction successfully.
- A 600-patient synthetic cohort was generated and the training/evaluation pipeline ran. Metrics are in `artifacts/models/v1/metrics.json`.

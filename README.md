# RenalTwin \| Kidney Health Digital Twin

> **Research prototype only. Not medical advice. Not clinically
> validated.**
>
> The default prediction model is trained on synthetic data and is
> intended for research/demo purposes.

## 1. Team Details

**Team Name:** `HealTech`

**Team Members:** - `Sinchana P` - `Sinchana J` -
`Pooja J` - `Rakshita Ravi Gadi`

**Team Contact:** `7892831836`

## 2. College / Incubator Information

**College / Institution:** `GSSS Institute for Engineering and Technology for Women (GSSSIETW), Mysuru`

**Department:** `Artificial Intelligence and Data Science (AI & DS)`

**Incubator / Innovation Centre:** `GSSS Technology Business Incubator Foundation`

## 3. Project Title

**RenalTwin \| Kidney Health Digital Twin**

RenalTwin is a research-oriented digital-twin prototype for kidney
health. It maintains a longitudinal patient representation from clinical
observations and uses available history to generate a 365-day renal-risk
prediction.

## 4. Problem Statement

Kidney health assessment involves reviewing multiple clinical
measurements collected at different points in time. Important indicators
such as eGFR, uACR, HbA1c, blood pressure, potassium, and hemoglobin can
change over time.

RenalTwin provides a single longitudinal representation of these
observations and a prototype risk-modelling workflow.

The system is designed to: - Store patient/twin information. - Capture
clinical observations over time. - Validate observation types, values,
units, and timestamps. - Determine whether sufficient eGFR history is
available. - Build the current twin state. - Generate a 365-day
renal-risk prediction when the required history is available. - Present
results through a dashboard. - Keep the prototype separate from clinical
diagnosis or medical decision-making.

## 5. Healthcare Use Case

RenalTwin is intended as a research and demonstration prototype for
exploring longitudinal kidney-health data and risk prediction.

### Example workflow

1.  Create a synthetic/de-identified patient twin.
2.  Enter demographic and risk-factor information.
3.  Add observations such as eGFR, uACR, HbA1c, hemoglobin, potassium,
    and clinic systolic blood pressure.
4.  Store observations with measurement date/time and provenance.
5.  Build the current twin state.
6.  Check data sufficiency and quality.
7.  Run the 365-day renal-risk prediction.
8.  Display risk probability, risk band, model version, and quality
    flags.

### Prediction readiness

The current backend requires at least two eGFR observations spanning at
least 60 days before prediction is considered ready.

## 6. Technical Stack

  Layer               Technology
  ------------------- ----------------------------------
  Language            Python
  Backend API         FastAPI
  API Server          Uvicorn
  Frontend            Streamlit
  Data Processing     Pandas, NumPy
  Database            SQLite
  ML                  Python-based prediction pipeline
  API Communication   HTTP / JSON

### Project structure

``` text
RenalTwin/
├── dashboard/
│   └── app.py
├── src/
│   └── renaltwin/
│       ├── api/
│       ├── db/
│       ├── data/
│       ├── ml/
│       ├── twin/
│       ├── egfr/
│       └── units/
└── ...
```

## 7. AI / ML Model or Framework Details

RenalTwin contains a prediction component that generates a **365-day
renal-risk probability**.

``` text
Patient/Twin Data
       ↓
Clinical Observations
       ↓
Validation + Unit Normalization
       ↓
Longitudinal Twin State
       ↓
Feature Construction
       ↓
Prediction Model
       ↓
365-Day Risk Probability
       ↓
Risk Band
```

The prediction API returns: - Risk probability - Risk band - Model
version - Feature set - Prediction status - Prediction horizon - Quality
flags

The current demonstration model uses synthetic data and is **not a
clinically validated risk calculator**.

## 8. Backend Architecture

The backend provides: - Twin creation and retrieval - Observation
ingestion - Observation validation - Unit conversion - Duplicate and
conflict detection - Out-of-order observation handling - Twin state
calculation - CKD stage derivation from eGFR - Prediction execution -
Prediction history

Prediction is only executed when the twin reaches an appropriate
prediction-ready state.

## 9. Data Model

### Twin

``` text
twin_id
display_name
age
sex
diabetes
hypertension
cvd
data_origin
state_version
created_at
```

### Supported observations

``` text
creatinine
egfr
uacr
hba1c
potassium
hemoglobin
sbp_clinic
hr_rest
sbp_home
sleep_min
steps
```

## 10. Data Quality and Validation

Incoming observations are validated for: - Supported observation type -
Correct observation category - Numeric values - Valid ranges - Timestamp
validity - UTC normalization - Unit conversion - Duplicate
observations - Conflicting observations - Out-of-order observations

Invalid observations are rejected and recorded in ingestion audit
information.

## 11. CKD / eGFR State

The prototype derives a CKD stage representation from the latest
available eGFR observation and reports: - Current twin status - State
version - Last eGFR timestamp - eGFR count in the relevant period -
Derived features - Data-quality flags

This output is informational and **not a clinical diagnosis**.

## 12. Frontend

The Streamlit dashboard provides a user-facing interface for: -
Creating/selecting a twin - Entering patient information - Adding
observations - Viewing current observations - Viewing twin state -
Running the 365-day prediction - Viewing the prediction result

The frontend communicates with the FastAPI backend rather than
implementing prediction logic independently.

## 13. Backend API

### Start the backend

``` bat
D:
cd \missalinious\RenalTwin_Working_Project\RenalTwin\RenalTwin
python -m uvicorn renaltwin.api.main:app --app-dir src --reload
```

Default API address:

``` text
http://127.0.0.1:8000
```

The API provides health/status, twin, observation, state, prediction,
and prediction-history operations.

## 14. Running the Dashboard

Open a second terminal:

``` bat
D:
cd \missalinious\RenalTwin_Working_Project\RenalTwin\RenalTwin
set PYTHONPATH=%CD%\src
streamlit run dashboard\app.py
```

The dashboard will normally be available at:

``` text
http://localhost:8501
```

Keep the backend terminal running while using the dashboard.

## 15. Example Demo Data

  Observation     Example Unit
  ------------- --------- ----------------
  eGFR                 72 mL/min/1.73 m²
  eGFR                 58 mL/min/1.73 m²
  uACR                145 mg/g
  HbA1c               7.1 \%
  Hemoglobin         12.8 g/dL
  Potassium           4.5 mmol/L
  Clinic SBP          138 mmHg

These are demonstration values only and are not medical recommendations.

## 16. 15--20 Minute Demo Video

**Demo Video:** [Google Drive Folder] `[[https://drive.google.com/drive/folders/18TkY7m7qhm3IRCK4_veW3Es5fQPzfCD-?usp=sharing\]`


## 17. Open-Source License Details

**License:** MIT License

Copyright (c) 2026 RenalTwin contributors.

This project is licensed under the MIT License. See the `LICENSE` file in the repository for the complete license text.

## 18. Architecture Diagram

**Architecture diagram:** [Google Drive Folder] `[https://drive.google.com/drive/folders/18TkY7m7qhm3IRCK4_veW3Es5fQPzfCD-?usp=sharing\]`


## 19. Presentation

**Presentation link:** `(https://drive.google.com/drive/folders/18TkY7m7qhm3IRCK4_veW3Es5fQPzfCD-?usp=sharing)`

## 20. Public Accessibility

All submission files and links should be publicly accessible without
additional permissions.


## 21. Limitations

RenalTwin is a **research prototype**.

-   The default model is trained on synthetic data.
-   The system is not clinically validated.
-   Predictions are not medical diagnoses.
-   Predictions should not be used for treatment decisions.
-   Real-world deployment would require clinical validation, security,
    privacy, governance, monitoring, and regulatory review.
-   Synthetic-data performance does not establish performance on real
    patient populations.

## 22. Future Scope

Potential future work: - Validation using appropriately governed
real-world datasets - Improved longitudinal feature engineering - Model
calibration and external validation - Explainable prediction
contributors - Patient-specific trend visualization - Healthcare
data-standard integration - Secure authentication and authorization -
Clinical workflow integration - Model monitoring and drift detection -
Prospective clinical evaluation


## 23. Disclaimer

**RenalTwin is a research prototype only. It is not medical advice, is
not clinically validated, and should not be used for diagnosis,
treatment, or clinical decision-making. The default demonstration model
is trained on synthetic data.**

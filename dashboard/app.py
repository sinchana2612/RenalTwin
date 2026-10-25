from __future__ import annotations

import os
from datetime import datetime, timezone, date, timedelta
from uuid import uuid4

import pandas as pd
import requests
import streamlit as st


# ============================================================
# CONFIG
# ============================================================

API_URL = os.getenv(
    "RENALTWIN_API_URL",
    "http://127.0.0.1:8000",
)

st.set_page_config(
    page_title="RenalTwin | Kidney Health Digital Twin",
    page_icon="🧬",
    layout="wide",
)


# ============================================================
# API HELPERS
# ============================================================

def api_request(
    method: str,
    path: str,
    **kwargs,
):
    url = f"{API_URL}{path}"

    try:
        response = requests.request(
            method,
            url,
            timeout=15,
            **kwargs,
        )

        try:
            data = response.json()
        except Exception:
            data = response.text

        if response.status_code >= 400:
            if isinstance(data, dict):
                error = data.get("error", {})
                message = error.get(
                    "message",
                    f"HTTP {response.status_code}",
                )
            else:
                message = str(data)

            st.error(message)
            return None

        return data

    except requests.exceptions.ConnectionError:
        st.error(
            "Cannot connect to the RenalTwin API. "
            "Make sure Uvicorn is running on "
            f"{API_URL}."
        )
        return None

    except requests.exceptions.RequestException as exc:
        st.error(f"API request failed: {exc}")
        return None


def get_twins():
    return api_request(
        "GET",
        "/api/v1/twins",
        params={"limit": 100},
    ) or []


def get_twin(twin_id: str):
    return api_request(
        "GET",
        f"/api/v1/twins/{twin_id}",
    )


def get_state(twin_id: str):
    return api_request(
        "GET",
        f"/api/v1/twins/{twin_id}/state",
    )


def get_observations(twin_id: str):
    return api_request(
        "GET",
        f"/api/v1/twins/{twin_id}/observations",
    ) or []


def get_risk_history(twin_id: str):
    return api_request(
        "GET",
        f"/api/v1/twins/{twin_id}/risk-history",
    ) or []


# ============================================================
# HEADER
# ============================================================

st.title("🧬 RenalTwin | Kidney Health Digital Twin")

st.caption(
    "Research prototype only. Not medical advice or clinically validated. "
    "Default model is trained on synthetic data."
)

health = api_request(
    "GET",
    "/api/v1/health",
)

if health:
    st.success(
        "Backend connected · synthetic and de-identified "
        "demonstration data only"
    )


# ============================================================
# MODEL STATUS
# ============================================================

with st.expander("Model status", expanded=False):

    model = api_request(
        "GET",
        "/api/v1/model/status",
    )

    if model:

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Model",
            model.get("version", "Unknown"),
        )

        c2.metric(
            "Feature set",
            model.get("feature_set", "Unknown"),
        )

        metrics = model.get("metrics", {})

        c3.metric(
            "Test AUROC",
            f"{metrics.get('test_auroc', 0):.3f}",
        )

        st.warning(
            "Synthetic simulator evaluation only; "
            "not clinical evidence."
        )


# ============================================================
# TWIN SELECTION
# ============================================================

st.header("Twin selection")

twins = get_twins()

if not twins:

    st.info(
        "No twins found. Create a new synthetic twin below."
    )

    selected_twin_id = None

else:

    twin_options = {
        f"{t.get('display_name', 'Unnamed')} "
        f"({t.get('twin_id', '')})": t.get("twin_id")
        for t in twins
    }

    selected_label = st.selectbox(
        "Select twin",
        list(twin_options.keys()),
    )

    selected_twin_id = twin_options[
        selected_label
    ]


# ============================================================
# CREATE TWIN
# ============================================================

with st.expander(
    "Create a new synthetic twin",
    expanded=not bool(selected_twin_id),
):

    with st.form("create_twin_form"):

        c1, c2, c3 = st.columns(3)

        with c1:
            display_name = st.text_input(
                "Display name",
                value="Synthetic Patient",
            )

            age = st.number_input(
                "Age",
                min_value=18,
                max_value=110,
                value=60,
                step=1,
            )

        with c2:

            sex = st.radio(
                "Sex",
                ["F", "M", "U"],
                horizontal=True,
            )

            diabetes = st.checkbox(
                "Diabetes",
                value=False,
            )

        with c3:

            hypertension = st.checkbox(
                "Hypertension",
                value=False,
            )

            cvd = st.checkbox(
                "Cardiovascular disease",
                value=False,
            )

        create = st.form_submit_button(
            "Create twin",
            type="primary",
        )

    if create:

        payload = {
            "display_name": display_name,
            "age_at_enrollment": age,
            "sex": sex,
            "diabetes": diabetes,
            "hypertension": hypertension,
            "cvd": cvd,
            "data_origin": "synthetic",
        }

        result = api_request(
            "POST",
            "/api/v1/twins",
            json=payload,
        )

        if result:

            st.success(
                f"Twin created: {result.get('twin_id')}"
            )

            st.rerun()


# ============================================================
# SELECTED TWIN
# ============================================================

if selected_twin_id:

    twin = get_twin(
        selected_twin_id
    )

    state = get_state(
        selected_twin_id
    )

    if twin:

        st.header("Twin overview")

        c1, c2, c3, c4, c5 = st.columns(5)

        c1.metric(
            "Age",
            twin.get(
                "age_at_enrollment",
                twin.get("age", "—"),
            ),
        )

        c2.metric(
            "Sex",
            twin.get("sex", "—"),
        )

        c3.metric(
            "Diabetes",
            "Yes"
            if twin.get("diabetes")
            else "No",
        )

        c4.metric(
            "Hypertension",
            "Yes"
            if twin.get("hypertension")
            else "No",
        )

        c5.metric(
            "CVD",
            "Yes"
            if twin.get("cvd")
            else "No",
        )


        if state:

            st.divider()

            c1, c2, c3, c4 = st.columns(4)

            c1.metric(
                "Twin status",
                state.get(
                    "status",
                    "Unknown",
                ),
            )

            c2.metric(
                "CKD stage",
                state.get(
                    "ckd_stage",
                    "Unknown",
                ),
            )

            counts = state.get(
                "counts",
                {},
            )

            c3.metric(
                "eGFR observations",
                counts.get(
                    "egfr_365d",
                    0,
                ),
            )

            c4.metric(
                "State version",
                state.get(
                    "state_version",
                    "—",
                ),
            )

            quality_flags = state.get(
                "quality_flags",
                [],
            )

            if quality_flags:

                st.info(
                    "Quality flags: "
                    + ", ".join(
                        quality_flags
                    )
                )


# ============================================================
# ADD CLINICAL OBSERVATIONS
# ============================================================

if selected_twin_id:

    st.header("Add clinical observations")

    st.write(
        "Enter multiple measurements below. "
        "No dropdown is required."
    )

    # Default rows
    default_rows = pd.DataFrame(
        [
            {
                "Observation": "egfr",
                "Value": 72.0,
                "Unit": "mL/min/1.73m²",
                "Observed date": date.today() - timedelta(days=90),
            },
            {
                "Observation": "egfr",
                "Value": 61.0,
                "Unit": "mL/min/1.73m²",
                "Observed date": date.today(),
            },
            {
                "Observation": "uacr",
                "Value": 145.0,
                "Unit": "mg/g",
                "Observed date": date.today(),
            },
            {
                "Observation": "hba1c",
                "Value": 7.1,
                "Unit": "%",
                "Observed date": date.today(),
            },
            {
                "Observation": "potassium",
                "Value": 4.5,
                "Unit": "mmol/L",
                "Observed date": date.today(),
            },
            {
                "Observation": "hemoglobin",
                "Value": 12.8,
                "Unit": "g/dL",
                "Observed date": date.today(),
            },
            {
                "Observation": "sbp_clinic",
                "Value": 138.0,
                "Unit": "mmHg",
                "Observed date": date.today(),
            },
        ]
    )

    edited = st.data_editor(
        default_rows,
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
        column_config={
            "Observation": st.column_config.TextColumn(
                "Observation",
                help=(
                    "Examples: egfr, uacr, hba1c, "
                    "potassium, hemoglobin, sbp_clinic"
                ),
                required=True,
            ),
            "Value": st.column_config.NumberColumn(
                "Value",
                required=True,
            ),
            "Unit": st.column_config.TextColumn(
                "Unit",
                required=True,
            ),
            "Observed date": st.column_config.DateColumn(
                "Observed date",
                required=True,
            ),
        },
        key="clinical_observations_editor",
    )

    st.caption(
        "Use lowercase observation names matching the "
        "RenalTwin clinical feature definitions."
    )

    submit_observations = st.button(
        "Submit all observations",
        type="primary",
        use_container_width=True,
    )

    if submit_observations:

        observations = []

        for _, row in edited.iterrows():

            obs_type = str(
                row["Observation"]
            ).strip().lower()

            if not obs_type:
                continue

            if pd.isna(row["Value"]):
                continue

            unit = str(
                row["Unit"]
            ).strip()

            if not unit:
                st.error(
                    f"Missing unit for {obs_type}."
                )
                st.stop()

            observation_date = row[
                "Observed date"
            ]

            if pd.isna(
                observation_date
            ):
                st.error(
                    f"Missing date for {obs_type}."
                )
                st.stop()

            if isinstance(
                observation_date,
                pd.Timestamp,
            ):
                observation_date = (
                    observation_date.date()
                )

            # Preserve the selected date while making a corrected same-day
            # measurement newer than its previous stored value.
            observed_at = datetime.now(timezone.utc).replace(
                year=observation_date.year,
                month=observation_date.month,
                day=observation_date.day,
            )

            observations.append(
                {
                    "obs_type": obs_type,
                    "value": float(
                        row["Value"]
                    ),
                    "unit": unit,
                    "observed_at":
                        observed_at.isoformat(),
                    "source_id": f"dashboard-{uuid4().hex}",
                    "provenance": "manual",
                }
            )

        if not observations:

            st.warning(
                "Enter at least one observation."
            )

        else:

            result = api_request(
                "POST",
                f"/api/v1/twins/"
                f"{selected_twin_id}/"
                f"clinical-observations",
                json=observations,
            )

            if result:

                st.success(
                    f"Submitted {len(observations)} "
                    "clinical observations."
                )

                st.rerun()


# ============================================================
# CURRENT OBSERVATIONS
# ============================================================

if selected_twin_id:

    st.header("Current observations")

    observations = get_observations(
        selected_twin_id
    )

    if observations:

        obs_df = pd.DataFrame(
            observations
        )

        display_columns = [
            column
            for column in [
                "obs_type",
                "value",
                "unit",
                "observed_at",
                "source_id",
                "provenance",
            ]
            if column in obs_df.columns
        ]

        st.dataframe(
            obs_df[display_columns],
            use_container_width=True,
            hide_index=True,
        )

    else:

        st.info(
            "No observations recorded for this twin."
        )


# ============================================================
# PREDICTION
# ============================================================

if selected_twin_id:

    st.header("Renal risk prediction")

    predict_button = st.button(
        "Run 365-day prediction",
        type="primary",
        use_container_width=True,
    )

    if predict_button:

        prediction = api_request(
            "POST",
            f"/api/v1/twins/"
            f"{selected_twin_id}/predict",
        )

        if prediction:

            probability = prediction.get(
                "risk_probability"
            )

            band = prediction.get(
                "risk_band",
                "unknown",
            )

            status = prediction.get(
                "status",
                "unknown",
            )

            if probability is not None:

                st.metric(
                    "Predicted 365-day risk",
                    f"{float(probability) * 100:.1f}%",
                )

            st.write(
                f"**Risk band:** {band}"
            )

            st.write(
                f"**Prediction status:** {status}"
            )

            st.caption(
                f"Model {prediction.get('model_version', '—')} · "
                f"Feature set {prediction.get('feature_set', '—')}"
            )

            st.caption(
                "Calculated from this twin's stored observations at "
                f"{prediction.get('as_of', 'unknown time')}."
            )

            with st.expander("Features used for this prediction"):
                st.json(prediction.get("features", {}))

            contributors = prediction.get(
                "top_contributors",
                [],
            )

            if contributors:

                st.subheader(
                    "Top contributors"
                )

                st.json(
                    contributors
                )

            flags = prediction.get(
                "quality_flags",
                [],
            )

            if flags:

                st.warning(
                    "Quality flags: "
                    + ", ".join(flags)
                )


# ============================================================
# RISK HISTORY
# ============================================================

if selected_twin_id:

    st.header("Risk history")

    history = get_risk_history(
        selected_twin_id
    )

    if history:

        history_df = pd.DataFrame(
            history
        )

        if (
            "as_of" in history_df.columns
            and "risk_probability"
            in history_df.columns
        ):

            chart_df = history_df[
                [
                    "as_of",
                    "risk_probability",
                ]
            ].copy()

            chart_df["risk_probability"] = (
                pd.to_numeric(
                    chart_df[
                        "risk_probability"
                    ],
                    errors="coerce",
                )
                * 100
            )

            chart_df = chart_df.set_index(
                "as_of"
            )

            st.line_chart(
                chart_df[
                    "risk_probability"
                ]
            )

        st.dataframe(
            history_df,
            use_container_width=True,
            hide_index=True,
        )

    else:

        st.info(
            "No predictions have been recorded yet."
        )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "RenalTwin is a research prototype using synthetic/"
    "de-identified demonstration data. "
    "Predictions are not medical advice and have not "
    "been clinically validated."
)

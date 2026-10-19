# API

Base path: `/api/v1`. Run `uvicorn renaltwin.api.main:app --port 8000`; interactive schema at `/docs`. Endpoints: `GET /health`, `GET /model/status`, `GET /data/status`, `POST /twins`, `GET /twins`, `GET /twins/{id}`, `POST /twins/{id}/clinical-observations`, `POST /twins/{id}/sensor-observations`, `GET /twins/{id}/observations`, `GET /twins/{id}/state`, `POST /twins/{id}/predict`, `GET /twins/{id}/risk-history`, `GET /twins/{id}/explanations/{prediction_id}`, `POST /twins/{id}/reset`, `DELETE /twins/{id}`. Request/response schemas are visible in OpenAPI.

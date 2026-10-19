FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
COPY configs ./configs
COPY dashboard ./dashboard
RUN pip install --no-cache-dir .[dashboard]
RUN useradd --create-home appuser && mkdir -p /app/artifacts /app/data && chown -R appuser:appuser /app
USER appuser
EXPOSE 8000
CMD ["uvicorn", "renaltwin.api.main:app", "--host", "0.0.0.0", "--port", "8000"]

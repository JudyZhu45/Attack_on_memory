FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY api ./api
COPY attacks ./attacks
COPY defenses ./defenses
COPY experiments ./experiments
COPY scripts ./scripts
COPY targets ./targets
COPY docs ./docs
COPY pyproject.toml README.md ./

EXPOSE 8000

CMD ["uvicorn", "api.server:app", "--host", "0.0.0.0", "--port", "8000"]

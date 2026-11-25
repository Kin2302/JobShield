FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    JAVA_HOME=/usr/lib/jvm/java-21 \
    JOBSHIELD_MODEL_DIR=/app/models/v3/jobshield-phobert-v3-typeA \
    JOBSHIELD_VNCORENLP_DIR=/app/models/vncorenlp

RUN apt-get update && apt-get install -y --no-install-recommends \
        openjdk-21-jre-headless \
        curl \
    && ln -sfn /usr/lib/jvm/java-21-openjdk-* /usr/lib/jvm/java-21 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt requirements-phobert.txt ./
RUN pip install --no-cache-dir --extra-index-url https://download.pytorch.org/whl/cpu \
        -r requirements-phobert.txt

COPY main.py phobert_v3_inference.py preprocessing_v3.py ./

RUN useradd --create-home --shell /bin/bash appuser \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 8001

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]

FROM python:3.11-slim

WORKDIR /app

# System requirements
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY starter_v0/requirements.txt /app/starter_v0/requirements.txt
RUN pip install --no-cache-dir -r /app/starter_v0/requirements.txt

# Copy application files
COPY starter_v0/ /app/starter_v0/

WORKDIR /app/starter_v0

EXPOSE 8501

ENV PYTHONUNBUFFERED=1 \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_SERVER_HEADLESS=true

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

CMD ["streamlit", "run", "app.py"]

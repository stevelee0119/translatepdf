FROM python:3.12-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends libgl1 libglib2.0-0 && \
    rm -rf /var/lib/apt/lists/*

RUN useradd -m -s /bin/bash appuser

WORKDIR /app

COPY requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt

COPY . ./
RUN chown -R appuser:appuser /app

USER appuser

EXPOSE 10000

CMD ["sh", "-c", "gunicorn api_server:app --bind 0.0.0.0:${PORT:-10000} --timeout 600 --workers 1"]

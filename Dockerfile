FROM mcr.microsoft.com/devcontainers/python:3.12

RUN apt-get update && \
    apt-get install -y --no-install-recommends libgl1 libglib2.0-0 && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

COPY requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt

COPY . ./
EXPOSE 7860

# Run Flask API server (for production deployment)
# For GitHub Pages, frontend is served from docs/ folder
CMD ["python", "api_server.py"]

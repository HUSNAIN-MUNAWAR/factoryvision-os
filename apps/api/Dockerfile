FROM python:3.12-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends libgl1 libglib2.0-0 && rm -rf /var/lib/apt/lists/*
COPY pyproject.toml README.md ./
COPY factoryvision factoryvision
COPY apps apps
RUN pip install --no-cache-dir .
CMD ["uvicorn","apps.api.main:app","--host","0.0.0.0","--port","8000"]

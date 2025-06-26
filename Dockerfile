FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    liblz4-dev \
    && rm -rf /var/lib/apt/lists/*

COPY reqs.txt .
RUN pip install --no-cache-dir -r reqs.txt

COPY . .

EXPOSE 3300

ENTRYPOINT ["python", "assetapi.py"]
# Step 1: Build dependencies. Making this 2 steps saves ~400MB
FROM python:3.13-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    liblz4-dev \
    && rm -rf /var/lib/apt/lists/*

COPY reqs.txt .
RUN pip install --no-cache-dir --prefix=/install -r reqs.txt

# Step 2: Runtime
FROM python:3.13-slim 

COPY --from=builder /install /usr/local

COPY . .

EXPOSE 3300

ENTRYPOINT ["python", "assetapi.py"]
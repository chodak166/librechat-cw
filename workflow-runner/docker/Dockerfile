# Use an official lightweight Python image.
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc \
        libc-dev \
        bash \
        sudo php cmake build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY docker/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

COPY . /app
RUN mv /app/workflows /app/workflows.default
RUN mv /app/dashboard /app/dashboard.default

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]



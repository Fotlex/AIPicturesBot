FROM python:3.12-slim-bookworm AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libjpeg-dev zlib1g-dev \
    netcat-openbsd \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY ./project/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.12-slim-bookworm AS runtime

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    netcat-openbsd \
    libjpeg62-turbo zlib1g \
    tzdata \
    gosu \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY . .

COPY .docker/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

RUN addgroup --system app && adduser --system --ingroup app app
RUN chown -R app:app /app
RUN mkdir -p /app/static /app/media/archives

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

EXPOSE 8000

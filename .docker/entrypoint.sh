#!/bin/sh
set -e

wait_for_port() {
    local host="$1"
    local port="$2"
    local service_name="$3"
    echo "Waiting for $service_name at $host:$port..."
    for i in $(seq 1 60); do
        if nc -z "$host" "$port" >/dev/null 2>&1; then
            echo "$service_name is up."
            return 0
        fi
        echo "Still waiting for $service_name at $host:$port..."
        sleep 1
    done
    echo "ERROR: $service_name not available after 60 seconds."
    return 1
}

wait_for_port "$POSTGRES_HOST" "$POSTGRES_PORT" "PostgreSQL"

wait_for_port "$REDIS_HOST" "$REDIS_PORT" "Redis"

echo "Fixing permissions for media and static files..."
chown -R app:app /app/static /app/media
echo "Permissions fixed."

exec gosu app "$@"

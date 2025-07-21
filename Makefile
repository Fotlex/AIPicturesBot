ENV=prod

COMPOSE_FILE = .docker/docker-compose.prod.yml
ENV_FILE = project/.env
DOCKER_COMPOSE = docker compose -f $(COMPOSE_FILE) --env-file $(ENV_FILE)

.PHONY: help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\036m%-30s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "To use 'prod' environment, append 'ENV=prod' (e.g., make up ENV=prod)"


# --------------- GENERAL COMMANDS --------------- #


.PHONY: build
build:
	@echo "Building Docker images for $(ENV) environment..."
	@$(DOCKER_COMPOSE) build

.PHONY: up
up:
	@echo "Starting Docker containers for $(ENV) environment..."
	@$(DOCKER_COMPOSE) up -d

.PHONY: up-logs
up-logs:
	@echo "Starting Docker containers with logs for $(ENV) environment..."
	@$(DOCKER_COMPOSE) up

.PHONY: logs
logs:
	@$(DOCKER_COMPOSE) logs -f

.PHONY: down
down:
	@echo "Stopping and removing Docker containers for $(ENV) environment..."
	@$(DOCKER_COMPOSE) down

.PHONY: clean
clean:
	@echo "WARNING: This will remove ALL containers, images, and volumes for $(ENV) environment. Data will be lost."
	@bash -c 'read -p "Are you sure? (y/N) " confirm; \
 	if [ "$$confirm" = "y" ]; then \
		echo "Proceeding with clean for $(ENV) environment..."; \
  		$(DOCKER_COMPOSE) down --rmi all -v --volumes --remove-orphans; \
 	else \
  		echo "Clean operation cancelled."; \
  		exit 1; \
 	fi'

.PHONY: restart
restart:
	@echo "Restarting Docker containers for $(ENV) environment..."
	@$(DOCKER_COMPOSE) restart


# --------------- BACKEND COMMANDS --------------- #


.PHONY: migrate
migrate:
	@echo "Running migrations for $(ENV) environment..."
	@$(DOCKER_COMPOSE) exec app python project/manage.py migrate --noinput

.PHONY: makemigrations
makemigrations:
	@echo "Running makemigrations for app(s): $(APP)..."
	@$(DOCKER_COMPOSE) exec app python project/manage.py makemigrations $(APP)

.PHONY: createsuperuser
createsuperuser:
	@echo "Creating superuser for $(ENV) environment..."
	@$(DOCKER_COMPOSE) exec app python project/manage.py createsuperuser

.PHONY: collectstatic
collectstatic:
	@echo "Collecting static files for $(ENV) environment..."
	@$(DOCKER_COMPOSE) exec app python project/manage.py collectstatic --noinput


.PHONY: base_commands
base_commands:
	@echo "Collecting static files for $(ENV) environment..."
	@$(DOCKER_COMPOSE) exec app python project/manage.py migrate --noinput
	@$(DOCKER_COMPOSE) exec app python project/manage.py collectstatic --noinput
	@$(DOCKER_COMPOSE) exec app python project/manage.py createsuperuser


.PHONY: shell
shell:
	@$(DOCKER_COMPOSE) exec app bash

.PHONY: dbshell
dbshell:
	@$(DOCKER_COMPOSE) exec app python project/manage.py dbshell

.PHONY: celery-worker-shell
celery-worker-shell:
	@$(DOCKER_COMPOSE) exec celery_worker bash

.PHONY: bot-shell
bot-shell:
	@$(DOCKER_COMPOSE) exec bot bash


# --------------- SSL/HTTPS COMMANDS --------------- #


CN ?= localhost

.PHONY: generate-self-signed-certs
generate-self-signed-certs:
	@echo "Checking for self-signed certificates for Common Name: $(CN)..."
	@mkdir -p .docker/nginx
	@if [ ! -f .docker/nginx/selfsigned.key ] || [ ! -f .docker/nginx/selfsigned.crt ]; then \
  		echo "Generating self-signed certificates..."; \
  		openssl req -x509 -nodes -days 3650 -newkey rsa:2048 \
   			-keyout .docker/nginx/selfsigned.key \
   			-out .docker/nginx/selfsigned.crt \
   			-subj "//CN=$(CN)"; \
  		echo "Certificates generated in .docker/nginx/"; \
	else \
  		echo "Self-signed certificates already exist in .docker/nginx/. If you wish to regenerate, remove them first."; \
	fi
	@chmod 600 .docker/nginx/selfsigned.key


.PHONY: get-certs
get-certs: 
	@echo "Attempting to obtain Let's Encrypt certificates for $(MAIN_DOMAIN)..."
	@$(DOCKER_COMPOSE) run --rm certbot certonly --webroot -w /var/www/certbot \
		--email $(LETSENCRYPT_EMAIL) --agree-tos --no-eff-email \
		-d $(MAIN_DOMAIN) $(addprefix -d ,$(filter-out $(MAIN_DOMAIN),$(subst ,,$(ALLOWED_HOSTS))))
	@echo "Reloading Nginx to pick up new certificates..."
	@$(DOCKER_COMPOSE) exec nginx nginx -s reload

.PHONY: renew-certs
renew-certs: 
	@echo "Attempting to renew Let's Encrypt certificates..."
	@$(DOCKER_COMPOSE) run --rm certbot renew
	@echo "Reloading Nginx to pick up renewed certificates..."
	@$(DOCKER_COMPOSE) exec nginx nginx -s reload

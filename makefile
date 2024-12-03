# Variables
COMPOSE_FILE=docker-compose.yml

# Build the Docker images
build:
	docker-compose -f $(COMPOSE_FILE) build

# Start the services
up:
	docker-compose -f $(COMPOSE_FILE) up -d

# Stop the services
down:
	docker-compose -f $(COMPOSE_FILE) down

# Restart the services
restart: down up

# Show the status of the services
status:
	docker-compose -f $(COMPOSE_FILE) ps

# Tail logs of the services
logs:
	docker-compose -f $(COMPOSE_FILE) logs -f

.PHONY: build up down restart status logs

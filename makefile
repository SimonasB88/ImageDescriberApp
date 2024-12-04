# Variables
COMPOSE_FILE=docker-compose.yml
CONTAINER_NAME=fastapi-container

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

# Run the tests
test:
	docker exec -i ${CONTAINER_NAME} sh -c "cd /app/app && pip install --upgrade httpx starlette && ls && pytest"

.PHONY: build up down restart status logs

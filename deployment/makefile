.PHONY: build network up down ps restart

# Pull latest image and build containers
build:
	docker pull lyikprodblueacr.azurecr.io/lyik-api:latest
	docker pull lyikprodblueacr.azurecr.io/w2w-spa:latest
	docker pull lyikprodblueacr.azurecr.io/lyik-admin:latest

	docker compose -f compose_lyik_stack.yml build

# Create Docker network if not exists
network:
	@if [ -z "$$(docker network ls --filter name=^net_lyik$$ -q)" ]; then \
		echo "Creating network net_lyik..."; \
		docker network create net_lyik; \
	else \
		echo "Network net_lyik already exists."; \
	fi

# Build and start all services
up: build network
	docker compose -f compose_lyik_stack.yml up -d

# Stop and remove containers
down:
	docker compose -f compose_lyik_stack.yml down

# Show running containers
ps:
	docker ps

# Restart all services
restart: down up

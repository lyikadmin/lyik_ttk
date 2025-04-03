.PHONY: build build-api build-ui network up down ps restart

# Pull all base images + build your own API
build: build-api build-ui

# Pull all base images, build api, and start containers
build-up: build up

# Build only lyik-api image
build-api:
	docker build -t lyik-api:latest -f Dockerfile .

# Pull latest tagged images for other services
build-ui:
	docker pull lyikprodblueacr.azurecr.io/w2w-spa:latest
	docker pull lyikprodblueacr.azurecr.io/lyik-admin:latest

# Create Docker network if not exists
network:
	@if [ -z "$$(docker network ls --filter name=^net_lyik$$ -q)" ]; then \
		echo "Creating network net_lyik..."; \
		docker network create net_lyik; \
	else \
		echo "Network net_lyik already exists."; \
	fi

# Start containers (assumes images are built)
up: network
	docker compose -f compose_lyik_stack.yml up -d

# Stop and remove containers
down:
	docker compose -f compose_lyik_stack.yml down

# Show running containers
ps:
	docker ps

# Restart all services
restart: down up

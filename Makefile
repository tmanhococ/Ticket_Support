# ============================================================
# Makefile — Convenience commands for Ticket Support project
# Usage: make <target>
# Note: On Windows, use Git Bash or WSL to run make commands
# ============================================================

.PHONY: build up down logs test restart ps help

## build: Build all Docker images
build:
	docker-compose build

## up: Start all services in detached mode
up:
	docker-compose up -d

## down: Stop and remove all containers
down:
	docker-compose down

## logs: Follow logs from all containers
logs:
	docker-compose logs -f

## restart: Restart all services
restart:
	docker-compose down && docker-compose up -d

## test: Run pytest inside the api container
test:
	docker-compose run --rm api pytest tests/ -v

## ps: Show status of running containers
ps:
	docker-compose ps

## help: Show this help message
help:
	@echo "Available targets:"
	@grep -E '^## ' Makefile | sed 's/## /  /'

.PHONY: help build up down logs ps test clean scale restart health

help:
	@echo "=========================================="
	@echo "Async Image Processing Pipeline"
	@echo "=========================================="
	@echo ""
	@echo "Available commands:"
	@echo ""
	@echo "  make build       - Build Docker images"
	@echo "  make up          - Start all services"
	@echo "  make down        - Stop all services"
	@echo "  make restart     - Restart all services"
	@echo "  make logs        - View all logs"
	@echo "  make ps          - Show service status"
	@echo "  make test        - Run API tests"
	@echo "  make clean       - Remove containers and volumes"
	@echo "  make scale       - Scale workers (use WORKERS=3)"
	@echo "  make health      - Check health endpoints"
	@echo "  make shell-api   - Open shell in API container"
	@echo "  make shell-worker- Open shell in worker container"
	@echo ""

build:
	docker-compose build

up:
	docker-compose up -d
	@echo ""
	@echo "✓ Services started"
	@echo "  API:      http://localhost:8000"
	@echo "  RabbitMQ: http://localhost:15672 (guest/guest)"
	@echo ""

down:
	docker-compose down

restart: down up

logs:
	docker-compose logs -f

ps:
	docker-compose ps

test:
	@echo "Running API tests..."
	@bash test_api.sh

clean:
	@echo "Removing all containers and volumes..."
	docker-compose down -v
	@echo "✓ Clean"

scale:
	@if [ -z "$(WORKERS)" ]; then \
		echo "Usage: make scale WORKERS=3"; \
		exit 1; \
	fi
	docker-compose up -d --scale resize_worker=$(WORKERS)
	@echo "✓ Scaled to $(WORKERS) resize workers"

restart: down up
	@echo "✓ Restarted"

health:
	@echo "Checking health endpoints..."
	@curl -s http://localhost:8000/health | python -m json.tool || echo "API not ready"
	@echo ""

shell-api:
	docker-compose exec api /bin/bash

shell-worker:
	docker-compose exec resize_worker_1 /bin/bash

validate:
	python validate_setup.py

logs-api:
	docker-compose logs -f api

logs-resize:
	docker-compose logs -f resize_worker_1

logs-thumbnail:
	docker-compose logs -f thumbnail_worker

logs-ocr:
	docker-compose logs -f ocr_worker

logs-ai:
	docker-compose logs -f ai_tagging_worker

logs-rabbitmq:
	docker-compose logs -f rabbitmq

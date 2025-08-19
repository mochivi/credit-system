.PHONY: help migrate migrate-generate migrate-upgrade migrate-downgrade migrate-current run-dev down-dev run-prod down-prod seed-dev migrate-history db-up db-down clean-dev produce-emotions

# Default target
help:
	@echo "Available commands:"
	@echo "  make migrate-generate DB_URL=<your DB URL> MIGRATION_NAME='description' - Generate a new migration from model changes"
	@echo "  make migrate-upgrade DB_URL=<your DB URL>                               - Apply all pending migrations"
	@echo "  make migrate-downgrade DB_URL=<your DB URL>                             - Rollback one migration"
	@echo "  make migrate-current DB_URL=<your DB URL>                               - Show current migration version"
	@echo "  make migrate-history DB_URL=<your DB URL>                               - Show migration history"
	@echo "  make db-up                                                              - Start database services; run migrations manually"
	@echo "  make db-down                                                            - Stop database services"
	@echo "  make seed-dev DB_URL=<your DB URL>                                      - Seed database with test data"
	@echo "  make run-dev                                                            - Run application"
	@echo "  make down-dev                                                           - Shutdown application"
	@echo "  make run-prod                                                           - Run application"
	@echo "  make down-prod                                                          - Shutdown application"
	@echo "  make clean-dev DB_URL=<your DB URL>                                     - Clean dev data"
	@echo "  make produce-emotions                                                   - Run emotional events producer script"
	@echo ""

# Start database services
db-up:
	docker compose up -d postgres redis

# Stop database services
db-down:
	docker compose down

# Generate a new migration
migrate-generate:
	@echo "Generating migration: $(MIGRATION_NAME)"
	@echo "Using DB_URL: $(DB_URL)"
	DB_URL=$(DB_URL) alembic revision --autogenerate -m "$(MIGRATION_NAME)"

# Apply all pending migrations
migrate-upgrade:
	@echo "Applying migrations..."
	@echo "Using DB_URL: $(DB_URL)"
	DB_URL=$(DB_URL) alembic upgrade head

# Rollback one migration
migrate-downgrade:
	@echo "Rolling back one migration..."
	@echo "Using DB_URL: $(DB_URL)"
	DB_URL=$(DB_URL) alembic downgrade -1

# Show current migration version
migrate-current:
	@echo "Current migration version:"
	@echo "Using DB_URL: $(DB_URL)"
	DB_URL=$(DB_URL) alembic current

# Show migration history
migrate-history:
	@echo "Migration history:"
	@echo "Using DB_URL: $(DB_URL)"
	DB_URL=$(DB_URL) alembic history

run-dev:
	@echo "Starting application in dev mode..."
	docker compose -f docker-compose.dev.yml up  --build

down-dev:
	@echo "Downing application"
	docker compose  -f docker-compose.dev.yml down

run-prod:
	@echo "Starting application with load balancer..."
	docker compose -f docker-compose.yml up --build

down-prod:
	@echo "Downing application"
	docker compose -f docker-compose.yml down

# Convenience target to generate and apply migrations
migrate: migrate-generate migrate-upgrade

# Seed deterministic dev/test data via script
seed-dev:
	@echo "Seeding dev data via script"
	DB_URL=$(DB_URL) SEED_DEV_DATA=1 python scripts/seed_dev.py --yes

clean-dev:
	@echo "Cleaning dev data via script"
	DB_URL=$(DB_URL) python scripts/clean_dev.py --yes

# Run the emotional events producer script
produce-emotions:
	@echo "Starting emotional events producer..."
	@if [ -n "$(RABBITMQ_HOST)" ]; then \
		echo "Using RabbitMQ host: $(RABBITMQ_HOST)"; \
		RABBITMQ_HOST=$(RABBITMQ_HOST) \
		RABBITMQ_USER=$(RABBITMQ_USER) \
		RABBITMQ_PASS=$(RABBITMQ_PASS) \
		RABBITMQ_PORT=$(RABBITMQ_PORT) \
		python scripts/produce_emotional_events.py; \
	else \
		echo "Using RabbitMQ settings from .env file"; \
		python scripts/produce_emotional_events.py; \
	fi

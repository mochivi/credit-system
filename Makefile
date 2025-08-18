.PHONY: help migrate migrate-generate migrate-upgrade migrate-downgrade migrate-current run down seed-dev migrate-history db-up db-down clean-dev produce-emotions

# Default target
help:
	@echo "Available commands:"
	@echo "  make migrate-generate MIGRATION_NAME=\"description\"  - Generate a new migration from model changes"
	@echo "  make migrate-upgrade DB_URL=\"your_db_url\"          - Apply all pending migrations"
	@echo "  make migrate-downgrade DB_URL=\"your_db_url\"        - Rollback one migration"
	@echo "  make migrate-current DB_URL=\"your_db_url\"          - Show current migration version"
	@echo "  make migrate-history DB_URL=\"your_db_url\"          - Show migration history"
	@echo "  make db-up                                           - Start database services; run migrations manually"
	@echo "  make db-down                                         - Stop database services"
	@echo "  make seed-dev DB_URL=\"postgresql+psycopg://user:pass@postgres-host:5432/db\" - Seed database for testing"
	@echo "  make run                                             - Run application"
	@echo "  make down                                            - Shutdown application"
	@echo "  make clean-dev DB_URL=\"postgresql+psycopg://user:pass@postgres-host:5432/db\" - Clean dev data"
	@echo "  make produce-emotions RABBITMQ_HOST=\"localhost\" RABBITMQ_USER=\"guest\" RABBITMQ_PASS=\"guest\" - Run emotional events producer"
	@echo ""
	@echo "Examples:"
	@echo "  make migrate-generate MIGRATION_NAME=\"add user table\""
	@echo "  make migrate-upgrade DB_URL=\"postgresql+psycopg://user:pass@postgres-host:5432/db\""

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

run:
	@echo "Starting application..."
	docker compose up --build

down:
	@echo "Downing application"
	docker compose down

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

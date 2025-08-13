.PHONY: help migrate migrate-generate migrate-upgrade migrate-downgrade migrate-current migrate-history db-up db-down

# Default target
help:
	@echo "Available commands:"
	@echo "  make migrate-generate MIGRATION_NAME=\"description\"  - Generate a new migration from model changes"
	@echo "  make migrate-upgrade DB_URL=\"your_db_url\"          - Apply all pending migrations"
	@echo "  make migrate-downgrade DB_URL=\"your_db_url\"        - Rollback one migration"
	@echo "  make migrate-current DB_URL=\"your_db_url\"          - Show current migration version"
	@echo "  make migrate-history DB_URL=\"your_db_url\"          - Show migration history"
	@echo "  make db-up            - Start database services"
	@echo "  make db-down          - Stop database services"
	@echo ""
	@echo "Examples:"
	@echo "  make migrate-generate MIGRATION_NAME=\"add user table\""
	@echo "  make migrate-upgrade DB_URL=\"postgresql+psycopg://user:pass@localhost:5432/db\""

# Start database services
db-up:
	docker-compose up -d postgres redis

# Stop database services
db-down:
	docker-compose down

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

# Convenience target to generate and apply migrations
migrate: migrate-generate migrate-upgrade

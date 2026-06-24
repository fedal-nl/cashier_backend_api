# Makefile for backend Django commands
# command to run: make {command name}

COMPOSE_FILE ?= ../docker-compose.yml
BACKEND_SERVICE ?= backend
DOCKER_COMPOSE = docker compose -f $(COMPOSE_FILE)
BACKEND_EXEC = $(DOCKER_COMPOSE) exec $(BACKEND_SERVICE)

.PHONY: help runserver migrations migrate test coverage lint format shell collectstatic

help:
	@echo "Available backend commands:"
	@echo "  make help          Show this help message"
	@echo "  make runserver     Run Django development server"
	@echo "  make migrations    Create Django migrations"
	@echo "  make migrate       Apply Django migrations"
	@echo "  make migrate-reports Apply Django migrations for reports database"
	@echo "  make test          Run Django tests"
	@echo "  make coverage      Run tests with coverage"
	@echo "  make lint          Run Ruff checks"
	@echo "  make format        Format code with Ruff"
	@echo "  make shell         Open Django shell"
	@echo "  make collectstatic Collect static files"
	@echo ""
	@echo "Options:"
	@echo "  COMPOSE_FILE       Docker compose file, default: ../docker-compose.yml"
	@echo "  BACKEND_SERVICE    Backend service name, default: backend"

runserver:
	$(BACKEND_EXEC) uv run python manage.py runserver 0.0.0.0:8000

migrations:
	$(BACKEND_EXEC) uv run python manage.py makemigrations

migrate:
	$(BACKEND_EXEC) uv run python manage.py migrate

migrate-reports:
	$(BACKEND_EXEC) uv run python manage.py migrate --database=reports

test:
	$(BACKEND_EXEC) uv run python manage.py test

coverage:
	$(BACKEND_EXEC) uv run coverage run manage.py test
	$(BACKEND_EXEC) uv run coverage report

lint:
	$(BACKEND_EXEC) uv run ruff check .

format:
	$(BACKEND_EXEC) uv run ruff format .

shell:
	$(BACKEND_EXEC) uv run python manage.py shell

collectstatic:
	$(BACKEND_EXEC) uv run python manage.py collectstatic --noinput

.PHONY: install run test lint security format migrate up down db-docs

install:
	uv sync

run:
	uv run fastapi dev app/main.py

test:
	uv run pytest

lint:
	uv run ruff check .
	uv run ruff format --check .
	uv run mypy app

security:
	uv run bandit -q -r app
	uv export --locked --no-dev --format requirements-txt --output-file /tmp/fastapi-template-requirements.txt
	uv run pip-audit --disable-pip --requirement /tmp/fastapi-template-requirements.txt

format:
	uv run ruff check --fix .
	uv run ruff format .

migrate:
	uv run alembic upgrade head

up:
	docker compose -f .docker/compose.yaml up --build

down:
	docker compose -f .docker/compose.yaml down

db-docs:
	uv run python -m tools.database.generate_erd

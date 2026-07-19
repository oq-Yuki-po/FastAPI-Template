.PHONY: install run test lint format migrate up down

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

format:
	uv run ruff check --fix .
	uv run ruff format .

migrate:
	uv run alembic upgrade head

up:
	docker compose -f .docker/compose.yaml up --build

down:
	docker compose -f .docker/compose.yaml down

.PHONY: install lint format test clean

# Default rule
all: install lint format test

install:
	uv sync

lint:
	uv run ruff check .

format:
	uv run black .

format-check:
	uv run black --check .
	uv run ruff check --select I .

test:
	uv run pytest

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	rm -rf .venv

.PHONY: help install install-dev test lint format clean run

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install production dependencies
	pip install -r requirements.txt

install-dev: ## Install development dependencies
	pip install -r requirements-dev.txt

test: ## Run tests
	@if [ -f env/bin/activate ]; then \
		. env/bin/activate && pytest; \
	else \
		echo "Virtual environment not found. Please run 'make setup' first."; \
		exit 1; \
	fi

lint: ## Run linting
	@if [ -f env/bin/activate ]; then \
		. env/bin/activate && black --check . --exclude="env/|venv/|.git/|__pycache__/|.mypy_cache/|.ruff_cache/"; \
		. env/bin/activate && isort --check-only . --skip-glob="env/*" --skip-glob="venv/*" --skip-glob=".git/*" --skip-glob="__pycache__/*" --skip-glob=".mypy_cache/*" --skip-glob=".ruff_cache/*"; \
		. env/bin/activate && flake8 . --exclude=env,venv,.git,__pycache__,.mypy_cache,.ruff_cache --max-line-length=88; \
	else \
		echo "Virtual environment not found. Please run 'make setup' first."; \
		exit 1; \
	fi

format: ## Format code
	@if [ -f env/bin/activate ]; then \
		. env/bin/activate && black . --exclude="env/|venv/|.git/|__pycache__/|.mypy_cache/|.ruff_cache/"; \
		. env/bin/activate && isort . --skip-glob="env/*" --skip-glob="venv/*" --skip-glob=".git/*" --skip-glob="__pycache__/*" --skip-glob=".mypy_cache/*" --skip-glob=".ruff_cache/*"; \
	else \
		echo "Virtual environment not found. Please run 'make setup' first."; \
		exit 1; \
	fi

clean: ## Clean up temporary files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/

run: ## Run the FastAPI application
	python main.py

run-dev: ## Run the FastAPI application in development mode
	uvicorn main:app --reload --host 0.0.0.0 --port 8000

pre-commit: ## Run pre-commit hooks on all files
	@if [ -f env/bin/activate ]; then \
		. env/bin/activate && pre-commit run --all-files; \
	else \
		echo "Virtual environment not found. Please run 'make setup' first."; \
		exit 1; \
	fi

pre-commit-install: ## Install pre-commit hooks
	@if [ -f env/bin/activate ]; then \
		. env/bin/activate && pre-commit install; \
	else \
		echo "Virtual environment not found. Please run 'make setup' first."; \
		exit 1; \
	fi

setup: install-dev pre-commit-install ## Setup development environment
	@echo "Development environment setup complete!"

check: lint test ## Run all checks (linting and tests)

# Celery commands
celery-worker: ## Start Celery worker
	@if [ -f env/bin/activate ]; then \
		. env/bin/activate && celery -A app.core.celery_app worker --loglevel=info; \
	else \
		echo "Virtual environment not found. Please run 'make setup' first."; \
		exit 1; \
	fi

celery-flower: ## Start Celery Flower monitoring
	@if [ -f env/bin/activate ]; then \
		. env/bin/activate && celery -A app.core.celery_app flower; \
	else \
		echo "Virtual environment not found. Please run 'make setup' first."; \
		exit 1; \
	fi

celery-beat: ## Start Celery beat scheduler
	@if [ -f env/bin/activate ]; then \
		. env/bin/activate && celery -A app.core.celery_app beat --loglevel=info; \
	else \
		echo "Virtual environment not found. Please run 'make setup' first."; \
		exit 1; \
	fi

redis-start: ## Start Redis server (if installed locally)
	redis-server

# Development with all services
dev-all: ## Start all development services (FastAPI, Celery, Redis)
	@echo "Starting all development services..."
	@echo "Make sure Redis is running: redis-server"
	@echo "In separate terminals run:"
	@echo "  make celery-worker"
	@echo "  make run-dev"

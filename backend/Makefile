.PHONY: help install dev test lint format clean

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(BLUE)Snaky Social Hub - Backend$(NC)"
	@echo ""
	@echo "$(GREEN)Usage:$(NC)"
	@echo "  make <target>"
	@echo ""
	@echo "$(GREEN)Targets:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-20s %s\n", $$1, $$2}'

install: ## Install dependencies with uv
	uv sync

dev: ## Run development server with hot reload
	uv run python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

dev-quiet: ## Run development server with minimal output
	@uv run python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000 2>&1 | grep -v "Uvicorn running\|Application startup complete"

test: ## Run all tests
	uv run pytest -v

test-quick: ## Run tests without verbose output
	uv run pytest

test-watch: ## Run tests in watch mode
	uv run pytest --watch

test-coverage: ## Run tests with coverage report
	uv run pytest --cov=app

lint: ## Check code with pylint
	uv run pylint app/

format: ## Format code with black
	uv run black app/ main.py

format-check: ## Check code formatting without changes
	uv run black --check app/ main.py

clean: ## Clean up cache and temporary files
	find . -type d -name __pycache__ -exec rm -r {} +
	find . -type d -name .pytest_cache -exec rm -r {} +
	find . -type d -name .venv -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name ".coverage*" -delete
	rm -rf htmlcov/
	rm -rf .mypy_cache/

db-reset: ## Reset the database (for development)
	@echo "Database has been reset on next server start (uses mock in-memory DB)"

info: ## Show project information
	@echo "$(BLUE)Backend Information$(NC)"
	@echo "Backend Path: ./backend"
	@echo "Framework: FastAPI"
	@echo "Python Version: 3.12"
	@echo "Package Manager: uv"
	@echo "Main File: main.py"
	@echo ""
	@echo "$(GREEN)Available Endpoints:$(NC)"
	@echo "  POST   /api/auth/signup"
	@echo "  POST   /api/auth/login"
	@echo "  POST   /api/auth/logout"
	@echo "  GET    /api/auth/me"
	@echo "  GET    /api/leaderboard"
	@echo "  POST   /api/leaderboard"
	@echo "  GET    /api/games"
	@echo "  GET    /api/games/{gameId}"
	@echo "  GET    /health"
	@echo ""
	@echo "$(GREEN)Documentation:$(NC)"
	@echo "  Swagger UI: http://localhost:8000/docs"
	@echo "  ReDoc:      http://localhost:8000/redoc"
	@echo "  OpenAPI:    http://localhost:8000/openapi.json"

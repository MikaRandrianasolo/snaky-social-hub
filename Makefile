.PHONY: help install dev test clean info

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(BLUE)Snaky Social Hub - Full Stack$(NC)"
	@echo ""
	@echo "$(GREEN)Usage:$(NC)"
	@echo "  make <target>"
	@echo ""
	@echo "$(GREEN)Main Targets:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -v "^_" | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-20s %s\n", $$1, $$2}'

install: ## Install dependencies for both frontend and backend
	@echo "$(BLUE)Installing frontend dependencies...$(NC)"
	cd frontend && npm install
	@echo "$(BLUE)Installing backend dependencies...$(NC)"
	cd backend && uv sync
	@echo "$(GREEN)✓ All dependencies installed$(NC)"

dev: ## Run both frontend and backend concurrently
	@echo "$(BLUE)Starting Snaky Social Hub...$(NC)"
	@echo "$(YELLOW)Frontend: http://localhost:8080$(NC)"
	@echo "$(YELLOW)Backend:  http://localhost:8000$(NC)"
	@echo "$(YELLOW)API Docs: http://localhost:8000/docs$(NC)"
	@echo ""
	cd frontend && npm run dev:all

dev-frontend: ## Run only frontend development server
	cd frontend && npm run dev

dev-backend: ## Run only backend development server
	cd backend && make dev

test: ## Run all tests (frontend and backend)
	@echo "$(BLUE)Running frontend tests...$(NC)"
	cd frontend && npm test
	@echo ""
	@echo "$(BLUE)Running backend tests...$(NC)"
	cd backend && uv run pytest -v

test-frontend: ## Run only frontend tests
	cd frontend && npm test

test-backend: ## Run only backend tests
	cd backend && uv run pytest -v

test-watch: ## Run frontend tests in watch mode
	cd frontend && npm run test:watch

lint: ## Run linters for both frontend and backend
	@echo "$(BLUE)Linting frontend...$(NC)"
	cd frontend && npm run lint
	@echo "$(BLUE)Linting backend...$(NC)"
	cd backend && make lint

format: ## Format code in both frontend and backend
	@echo "$(BLUE)Formatting frontend...$(NC)"
	cd frontend && npm run format || echo "Frontend formatting not configured"
	@echo "$(BLUE)Formatting backend...$(NC)"
	cd backend && make format

clean: ## Clean up all dependencies and cache
	@echo "$(BLUE)Cleaning frontend...$(NC)"
	cd frontend && rm -rf node_modules .dist dist .next
	@echo "$(BLUE)Cleaning backend...$(NC)"
	cd backend && make clean
	@echo "$(GREEN)✓ Cleanup complete$(NC)"

reset: clean install ## Clean everything and reinstall (fresh start)
	@echo "$(GREEN)✓ Project reset complete$(NC)"

info: ## Show project information
	@echo "$(BLUE)Snaky Social Hub - Project Information$(NC)"
	@echo ""
	@echo "$(GREEN)Frontend$(NC)"
	@echo "  Location:  frontend/"
	@echo "  Framework: React + TypeScript + Vite"
	@echo "  Port:      8080"
	@echo "  Commands:"
	@echo "    make dev-frontend   - Run frontend only"
	@echo "    make test-frontend  - Test frontend only"
	@echo ""
	@echo "$(GREEN)Backend$(NC)"
	@echo "  Location:  backend/"
	@echo "  Framework: FastAPI + Python"
	@echo "  Port:      8000"
	@echo "  DB:        Mock in-memory"
	@echo "  Commands:"
	@echo "    make dev-backend    - Run backend only"
	@echo "    make test-backend   - Test backend only"
	@echo "    cd backend && make help - See all backend commands"
	@echo ""
	@echo "$(GREEN)Full Stack Commands$(NC)"
	@echo "  make dev             - Run both frontend and backend"
	@echo "  make test            - Test both frontend and backend"
	@echo "  make install         - Install all dependencies"
	@echo ""
	@echo "$(GREEN)URLs$(NC)"
	@echo "  Frontend:   http://localhost:8080"
	@echo "  Backend:    http://localhost:8000"
	@echo "  API Docs:   http://localhost:8000/docs"
	@echo "  API ReDoc:  http://localhost:8000/redoc"
	@echo ""

status: ## Check if servers are running
	@echo "$(BLUE)Checking services...$(NC)"
	@bash -c 'curl -s http://localhost:8000/health > /dev/null && echo "$(GREEN)✓ Backend$(NC)" || echo "$(YELLOW)✗ Backend$(NC)"' || true
	@bash -c 'curl -s http://localhost:8080 > /dev/null && echo "$(GREEN)✓ Frontend$(NC)" || echo "$(YELLOW)✗ Frontend$(NC)"' || true

.PHONY: help install dev dev-frontend dev-backend test test-frontend test-backend test-watch lint format clean reset info status

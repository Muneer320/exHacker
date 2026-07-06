# Makefile — exHacker development commands

.PHONY: setup dev test lint clean docker-up docker-down

# ─── Setup ──────────────────────────────────────────────────────────────────

setup: ## Install all dependencies and initialize the project
	@echo "Setting up backend..."
	cd backend && uv venv && uv pip install -e ".[dev]"
	@echo "Setting up frontend..."
	cd frontend && npm install
	@echo "Creating .env from .env.example..."
	cp -n .env.example .env 2>/dev/null || true
	@echo "Running database migrations..."
	cd backend && alembic upgrade head
	@echo "Setup complete! Run 'make dev' to start."

# ─── Development ─────────────────────────────────────────────────────────────

dev: ## Start backend and frontend dev servers
	@echo "Starting backend (http://localhost:8000)..."
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
	@sleep 2
	@echo "Starting frontend (http://localhost:3000)..."
	cd frontend && npm run dev

dev-backend: ## Start backend only
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend: ## Start frontend only
	cd frontend && npm run dev

# ─── Testing ────────────────────────────────────────────────────────────────

test: ## Run all tests
	cd backend && pytest -v --cov=app
	cd frontend && npm test

test-backend: ## Run backend tests only
	cd backend && pytest -v --cov=app

test-frontend: ## Run frontend tests only
	cd frontend && npm test

# ─── Linting ────────────────────────────────────────────────────────────────

lint: ## Run all linters
	cd backend && ruff check . && mypy app
	cd frontend && npm run lint

lint-backend: ## Lint backend only
	cd backend && ruff check . && mypy app

lint-frontend: ## Lint frontend only
	cd frontend && npm run lint

format: ## Format all code
	cd backend && ruff format .
	cd frontend && npm run format

# ─── Database ───────────────────────────────────────────────────────────────

migrate: ## Run database migrations
	cd backend && alembic upgrade head

rollback: ## Rollback last migration
	cd backend && alembic downgrade -1

revision: ## Create new migration
	cd backend && alembic revision --autogenerate -m "$(message)"

seed: ## Load seed data
	cd backend && python scripts/seed_data.py

# ─── Docker ─────────────────────────────────────────────────────────────────

docker-up: ## Start Docker services
	docker compose up --build -d

docker-down: ## Stop Docker services
	docker compose down

docker-logs: ## View Docker logs
	docker compose logs -f

# ─── Cleanup ────────────────────────────────────────────────────────────────

clean: ## Clean build artifacts
	rm -rf backend/**/__pycache__ backend/.venv
	rm -rf frontend/node_modules frontend/.next
	rm -f backend/*.db backend/*.sqlite
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

# ─── Help ───────────────────────────────────────────────────────────────────

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

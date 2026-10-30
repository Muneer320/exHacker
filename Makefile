.PHONY: setup test lint dev-backend dev-frontend migrate docker-up docker-down docker-verify

setup:
	cd backend && uv sync --extra dev
	cd frontend && npm ci

dev-backend:
	cd backend && uv run uvicorn app.main:app --reload

dev-frontend:
	cd frontend && npm run dev

test:
	cd backend && uv run pytest -q
	cd frontend && npm run typecheck
	cd frontend && npm test

lint:
	cd backend && uv run ruff check app tests migrations ../scripts
	cd frontend && npm run lint

migrate:
	cd backend && uv run alembic upgrade head

docker-up:
	docker compose up --build -d

docker-down:
	docker compose down

docker-verify:
	docker compose -p exhacker-verify -f compose.verify.yml up --build --wait
	docker compose -p exhacker-verify -f compose.verify.yml run --rm --build backend-tests
	python scripts/verify_docker.py --restart

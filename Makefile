.PHONY: backend-dev frontend-dev test test-backend test-frontend lint format typecheck build db-upgrade db-seed up down

backend-dev:
	uvicorn app.main:app --app-dir backend --reload

frontend-dev:
	pnpm --dir frontend dev

test:
	$(MAKE) test-backend
	$(MAKE) test-frontend

test-backend:
	pytest --cov=backend/app --cov-report=term-missing

test-frontend:
	pnpm --dir frontend test

lint:
	ruff check backend
	pnpm --dir frontend lint

format:
	ruff format --check backend
	pnpm --dir frontend format

typecheck:
	mypy backend/app
	pnpm --dir frontend typecheck

db-upgrade:
	alembic -c backend/alembic.ini upgrade head

db-seed:
	python scripts/seed_demo.py --with-database

build:
	pnpm --dir frontend build

up:
	docker compose up --build

down:
	docker compose down

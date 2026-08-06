.PHONY: setup dev test lint format down

setup:
	python3 -m venv apps/api/.venv && apps/api/.venv/bin/pip install -e 'apps/api[dev]'
	corepack pnpm install

dev:
	docker compose up --build

test:
	apps/api/.venv/bin/pytest apps/api/tests

lint:
	apps/api/.venv/bin/ruff check apps/api
	corepack pnpm --dir apps/web lint

format:
	apps/api/.venv/bin/ruff format apps/api
	corepack pnpm --dir apps/web format

down:
	docker compose down

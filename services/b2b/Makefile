up:
	docker-compose up -d

down:
	docker-compose down

build:
	docker-compose build 

rebuild:
	docker-compose down
	docker-compose build 
	docker-compose up -d

migrate:
	docker-compose exec b2b-backend uv run alembic -c /app/database/alembic.ini upgrade head

migration:
	docker-compose exec b2b-backend uv run alembic -c /app/database/alembic.ini revision --autogenerate -m "$(name)"

format:
	uv run ruff format .
	uv run ruff check . --fix

check:
	uv run ruff check .

test:
	uv run python -m pytest -q

seed:
	docker-compose exec b2b-backend uv run python ./scripts/seed.py

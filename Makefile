.PHONY: up down restart logs migrate rollback shell

install:
	pip install -r requirements.txt

up:
	docker compose up --build

down:
	docker compose down

restart:
	docker compose restart

logs:
	docker compose logs -f

migrate:
	docker compose exec app alembic upgrade head

rollback:
	docker compose exec app alembic downgrade -1

shell:
	docker compose exec app python

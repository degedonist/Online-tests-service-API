.PHONY: up down restart logs migrate rollback shell

install:
	pip install -r requirements.txt

up:
	docker compose up -d && echo "📄 Swagger docs: http://localhost:8000/docs"

down:
	docker compose down

restart:
	docker compose restart && echo "📄 Swagger docs: http://localhost:8000/docs"

logs:
	docker compose logs -f

migrate:
	docker compose exec app alembic upgrade head

rollback:
	docker compose exec app alembic downgrade -1

shell:
	docker compose exec app python

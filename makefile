MESSAGE ?=hello world
ALEMBIC_MAKEMIGRATION = uv run alembic revision --autogenerate -m 
ALEMBIC_MIGRATE = uv run alembic upgrade head

migration:
	@echo "Enter migration message: "; \
	read user_input; \
	$(ALEMBIC_MAKEMIGRATION) "$$user_input"

migrate:
	$(ALEMBIC_MIGRATE)

migrate_in_test:
	CONFIG_FILE=config.test.toml $(ALEMBIC_MIGRATE)

run_tests:
	uv run pytest

run_server:
	uvicorn main:app --reload
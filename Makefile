.PHONY: run lint test

run:
	poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

lint:
	poetry run black .

test:
	PYTHONPATH=. poetry run pytest

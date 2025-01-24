.PHONY: run lint test

shell:
	poetry shell
run:
	poetry run python app/main.py

lint:
	poetry run black .

test:
	PYTHONPATH=. poetry run pytest

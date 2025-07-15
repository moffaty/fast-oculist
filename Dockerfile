FROM python:3.11-slim
RUN apt update && apt install -y libpq-dev gcc
RUN pip install -U pip poetry==1.8.5
WORKDIR /app
COPY poetry.lock pyproject.toml ./
RUN poetry config virtualenvs.create false && poetry install --without dev
COPY ./ ./
ENTRYPOINT ["python", "app/main.py"]
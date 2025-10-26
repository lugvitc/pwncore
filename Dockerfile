FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends build-essential gcc python3-dev
WORKDIR /app

RUN pip install poetry

RUN poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock README.md /app/
# RUN poetry install

# Copy everything from src into /app/src
COPY src /app/src
RUN poetry install

WORKDIR /app/src

WORKDIR /app/src

EXPOSE 8000
EXPOSE 8081
# Run both main app and admin app
CMD ["sh", "-c", "gunicorn -w 4 -k uvicorn.workers.UvicornWorker pwncore:app --bind 0.0.0.0:8000 --log-level debug & uvicorn pwncore.admin_app:admin_app --host 0.0.0.0 --port 8081 & wait"]
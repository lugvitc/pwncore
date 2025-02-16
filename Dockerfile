FROM python:3.12-slim

WORKDIR /app

RUN pip install poetry

RUN poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock README.md /app/
# RUN poetry install

# Copy everything from src into /app/src
COPY src /app/src
RUN poetry install

WORKDIR /app/src

EXPOSE 8000

# Run FastAPI with Gunicorn
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "pwncore:app", "--bind", "0.0.0.0:8000", "--log-level", "debug"]


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

ENV PORT=${PORT:-8000}
ENV WORKERS=${WORKERS:-4}
EXPOSE ${PORT}

CMD ["bash", "-c", "gunicorn -w ${WORKERS} -k uvicorn.workers.UvicornWorker pwncore:app --bind 0.0.0.0:${PORT} --log-level debug"]
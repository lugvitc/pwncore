# CTF Backend

## Tech Stack:

-   Framework: **FastAPI**
-   Database: **PostgreSQL (ORM: Tortoise)**
-   Server: **Uvicorn**
-   Test: **TestClient (in FastAPI) / Tox**
-   Containerization: **Docker**
-   CI/CD: **Github Actions** and ship to **Github packages**

## Setup:

```sh
pip install poetry
python -m venv .venv                # Create a python virtual environment
source .venv/bin/activate           # Activate it (This command will differ for Windows)
poetry install                      # Install the dependencies
```

## Run:

```sh
python -m uvicorn pwncore:app --reload
```

## Testing:

Take a look at `tests/test_login.py` as an example on writing tests.

A Github Workflow is set to automatically run pytest on all filenames beginning with `test` under tox. Regardless, you might want to run the tests on your machine locally before pushing:

```sh
tox
```

## Structure:

To make the API routes clear without having to check each file, we organise the routes in separate python files.

Each file has their own router, eg. `/team`, with endpoints lying under it: `/team/list` `/team/login`

All individual routes (`/team/*`, `/ctf/*`) are then put behind `/api` in the `routes/__init__.py`, so we end up with `/api/team/*` and `/api/ctf*`.

In case a certain route has multiple complex tasks, they can be separated as a submodule. For example, the route `/api/ctf/start` will perform a lot of tasks (interacting with docker etc.), and hence has a separate file for it.

`src/`:

```
docs.py                     # Takes metadata from each route and compiles it for FastAPI
config.py                   # Configuration variables
db.py                       # Database schemas and connector

routes/
    L team.py
    L ctf/
        L start.py          # Separate file since it involves much more complex tasks
        L __init__.py       # Rest of the ctf routes go here
    L admin.py
    L leaderboard.py
    L team.py
    L __init__.py           # Main router under `/api`, any misc routes go here
tests/
```

## Documenting:

FastAPI generates documentation for the routes using OpenAPI. The documentation is available by default at `/docs` (Swagger UI) and `/redoc` (ReDoc).

There are 2 ways to add documentation for a route:

1. Explicitly mention the summary and description:

```py
@router.get("/start/{ctf_id}",
    description="This description supports **Markdown**.",
    summary="Start the docker container"
)
```

2. Let it infer summary from function name and description from comments:

```py
@router.get("/start/{ctf_id}")
async def start_the_docker_container(ctf_id: int):       # The function name is inferred for the summary
    # This is a regular single-line comment.
    # Will not be displayed in the documentation.
    '''
    This is a multi-line comment, and will be displayed
    in the documentation when the route is expanded.

    The cool thing is that Markdown works here!
    # See, Markdown works!
    _Pretty_ **cool** right?
    '''
    return {"status": "CTF started"}
```

Result:

![Result](.github/route_docs.png)

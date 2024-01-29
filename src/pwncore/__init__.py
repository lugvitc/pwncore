from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from tortoise import Tortoise

import pwncore.docs as docs
import pwncore.routes as routes

from pwncore.container import docker_client
from pwncore.config import config
from pwncore.models import Container


@asynccontextmanager
async def app_lifespan(app: FastAPI):
    # Startup
    await Tortoise.init(db_url=config.db_url, modules={"models": ["pwncore.models"]})
    await Tortoise.generate_schemas()

    yield
    # Shutdown
    # Stop and remove all running containers
    containers = await Container.all().values()
    await Container.all().delete()
    for db_container in containers:
        try:
            container = await docker_client.containers.get(db_container["docker_id"])
            await container.kill()
            await container.delete()
        except (
            Exception
        ):  # Raises DockerError if container does not exist, just pass for now.
            pass

    # close_connections is deprecated, not sure how to use connections.close_all()
    await Tortoise.close_connections()
    await docker_client.close()


app = FastAPI(
    title="Pwncore",
    openapi_tags=docs.tags_metadata,
    description=docs.description,
    lifespan=app_lifespan,
)
app.include_router(routes.router)

origins = [
    "http://ctf.lugvitc.org",
    "https://ctf.lugvitc.org",
]

if config.development:
    origins.append("http://localhost:5173")
    origins.append("http://localhost:4173")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

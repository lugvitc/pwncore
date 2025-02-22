from contextlib import asynccontextmanager

import shutil
import aiodocker
from logging import getLogger
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from tortoise import Tortoise

import pwncore.containerASD as containerASD
import pwncore.docs as docs
import pwncore.routes as routes
from pwncore.config import config
from pwncore.models import Container

logger = getLogger(__name__)

@asynccontextmanager
async def app_lifespan(app: FastAPI):
    # Startup
    await Tortoise.init(db_url=config.db_url, modules={"models": ["pwncore.models"]})
    await Tortoise.generate_schemas()

    containerASD.docker_client = aiodocker.Docker(url=config.docker_url)

    yield
    # Shutdown
    # Stop and remove all running containers
    containers = await Container.all().values()
    await Container.all().delete()
    for db_container in containers:
        try:
            container = await containerASD.docker_client.containers.get(
                db_container["docker_id"]
            )
            await container.kill()
            await container.delete()
        except (
            Exception
        ):  # Raises DockerError if container does not exist, just pass for now.
            pass
    try:
        shutil.rmtree(config.staticfs_data_dir)
    except Exception as err:
        logger.exception("Failed to delete static files", exc_info=err)

    # close_connections is deprecated, not sure how to use connections.close_all()
    await Tortoise.close_connections()
    await containerASD.docker_client.close()


app = FastAPI(
    title="Pwncore",
    openapi_tags=docs.tags_metadata,
    description=docs.description,
    lifespan=app_lifespan,
)
app.include_router(routes.router)

origins = [
    "http://c0d.lugvitc.net",
    "https://c0d.lugvitc.net",
]

if config.development:
    origins.append("*")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

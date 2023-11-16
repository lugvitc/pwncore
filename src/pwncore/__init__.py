from fastapi import FastAPI
from contextlib import asynccontextmanager

from tortoise.contrib.fastapi import register_tortoise

import pwncore.docs as docs
import pwncore.routes as routes
from pwncore.container import docker_client
from pwncore.config import config


@asynccontextmanager
async def app_lifespan(app: FastAPI):
    # Startup
    register_tortoise(
        app,
        db_url=config.db_url,
        modules={"models": ["pwncore.models"]},
        generate_schemas=True,
        add_exception_handlers=True,
    )
    yield
    # Shutdown
    await docker_client.close()


app = FastAPI(
    title="Pwncore",
    openapi_tags=docs.tags_metadata,
    description=docs.description,
    lifespan=app_lifespan,
)
app.include_router(routes.router)

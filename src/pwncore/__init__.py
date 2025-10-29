import shutil
from contextlib import asynccontextmanager
from logging import getLogger

import aiodocker
import jwt
from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from tortoise import Tortoise

import pwncore.containerASD as containerASD
import pwncore.docs as docs
import pwncore.routes as routes
from pwncore.config import config
from pwncore.models import Container
from pwncore.routes.auth import JwtInfo

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


@app.middleware("http")
async def check_blacklist(
    request: Request,
    call_next,  # noqa: ANN001
):
    """Middleware to handle bans."""
    try:
        token = request.headers["authorization"].split(" ")[1]  # Remove Bearer

        decoded_token: JwtInfo = jwt.decode(
            token,
            config.jwt_secret,
            algorithms=["HS256"],
        )
        team_id = decoded_token["team_id"]
        if team_id in config.blacklist:
            return Response(status_code=status.HTTP_403_FORBIDDEN)
    except KeyError:
        pass
    except jwt.exceptions.InvalidTokenError:
        pass
    return await call_next(request)

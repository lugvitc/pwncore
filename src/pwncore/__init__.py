from fastapi import FastAPI

import pwncore.docs as docs
import pwncore.routes as routes

app = FastAPI(
    title="Pwncore",
    openapi_tags=docs.tags_metadata,
    description=docs.description
)

app.include_router(routes.router)

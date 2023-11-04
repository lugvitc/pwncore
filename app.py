from fastapi import FastAPI

import docs
import routes

app = FastAPI(openapi_tags=docs.tags_metadata, description=docs.description)

app.include_router(routes.router)

a = 0

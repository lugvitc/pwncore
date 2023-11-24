from fastapi import APIRouter

from pwncore.routes import ctf, team
from pwncore.config import config

# Main router (all routes go under /api)
router = APIRouter(prefix="/api")

# Include all the subroutes
router.include_router(ctf.router)
router.include_router(team.router)

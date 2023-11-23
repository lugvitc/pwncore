from fastapi import APIRouter

from pwncore.routes import ctf, team, auth

# Main router (all routes go under /api)
router = APIRouter(prefix="/api")

# Include all the subroutes
router.include_router(auth.router)
router.include_router(ctf.router)
router.include_router(team.router)

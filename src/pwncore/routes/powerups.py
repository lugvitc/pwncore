from fastapi import APIRouter, HTTPException

from pwncore.config import config
from pwncore.models import Powerup, PowerupType, Team
from pwncore.routes.auth import RequireJwt

metadata = {"name": "powerups", "description": "Powerups for teams"}
router = APIRouter(prefix="/powerups", tags=["team"])


@router.get("/view")
async def view_powerups(jwt: RequireJwt):
    # Return available powerups list
    pass


@router.post("/use/{powerup_type}")
async def use_powerup(powerup_type: PowerupType, jwt: RequireJwt):
    # Define logic to use available powerups and deduct points
    pass


@router.get("/about/{powerup_type}")
async def get_about_powerups(powerup_type: PowerupType, jwt: RequireJwt):
    # Return the about of the powerup
    pass


async def lucky_draw(team: Team):
    # Lucky draw logic
    pass


async def sabotage(team: Team):
    # Sabotage logic
    pass


async def gamble(team: Team):
    # Gamble logic
    pass


async def point_siphon(team: Team):
    # Point Siphon logic
    pass

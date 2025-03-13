
from tortoise.contrib.pydantic.creator import pydantic_model_creator
from fastapi import APIRouter, HTTPException, Response

from pwncore.config import config
from pwncore.models import (
    Powerup, 
    PowerupType, 
    Team,
    AttackDefTeam,
    UsedPowerup,
    Powerup_Pydantic,
)
from pwncore.routes.auth import RequireJwt

metadata = {"name": "powerups", "description": "Powerups for teams"}
router = APIRouter(prefix="/powerups", tags=["team"])

@router.get("/remaining")
async def view_remaining_powerups(jwt: RequireJwt, response: Response):
    team_id = jwt["team_id"]
    attack_def_team = await AttackDefTeam.get(team_id=team_id)
    if (attack_def_team is None):
        return {"msg_code": config.msg_codes["attack_def_team_not_found"]}
    return await Powerup_Pydantic.from_queryset(await attack_def_team.remaining_powerups())

@router.get("/used")
async def view_used_powerups(jwt: RequireJwt):
    team_id = jwt["team_id"]
    attack_def_team = await AttackDefTeam.get(team_id=team_id)
    if (attack_def_team is None):
        return {"msg_code": config.msg_codes["attack_def_team_not_found"]}
    
    used_powerups = UsedPowerup.filter(powerup__attack_def_team=attack_def_team.id).prefetch_related("powerup")
    return await used_powerups


# @router.post("/use/{powerup_type}")
# async def use_powerup(powerup_type: PowerupType, jwt: RequireJwt):
    # Define logic to use available powerups and deduct points
    # pass


# @router.get("/about/{powerup_type}")
# async def get_about_powerups(powerup_type: PowerupType, jwt: RequireJwt):
    # Return the about of the powerup
    # pass


# async def lucky_draw(team: Team):
#     # Lucky draw logic
#     pass


# async def sabotage(team: Team):
#     # Sabotage logic
#     pass


# async def gamble(team: Team):
#     # Gamble logic
#     pass


# async def point_siphon(team: Team):
#     # Point Siphon logic
#     pass

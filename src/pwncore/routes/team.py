from __future__ import annotations

from fastapi import APIRouter, Response
from pwncore.models import Team, User
from pwncore.config import config

# Metadata at the top for instant accessibility
metadata = {"name": "team", "description": "Operations with teams"}

router = APIRouter(prefix="/team", tags=["team"])


@router.get("/list")
async def team_list(response: Response):
    teams = await Team.all().values()
    return teams


@router.get("/login")
async def team_login():
    # Do login verification here
    return {"status": "logged in!"}


# Unable to test as adding users returns an error
@router.get("/members/{team_id}")
async def team_members(team_id: int, response: Response):
    members = await User.filter(team_id=team_id).values()
    # Incase of no members, it just returns an empty list.
    return members

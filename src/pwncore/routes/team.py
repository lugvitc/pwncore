from __future__ import annotations

from fastapi import APIRouter, Response
from pwncore.models import Team, User, Team_Pydantic, User_Pydantic
from pwncore.config import config

# Metadata at the top for instant accessibility
metadata = {"name": "team", "description": "Operations with teams"}

router = APIRouter(prefix="/team", tags=["team"])


@router.get("/list")
async def team_list(response: Response):
    teams = await Team_Pydantic.from_queryset(Team.all())
    return teams


@router.get("/login")
async def team_login():
    # Do login verification here
    return {"status": "logged in!"}


# Unable to test as adding users returns an error
@router.get("/members/{team_id}")
async def team_members(team_id: int, response: Response):
    members = await User_Pydantic.from_queryset(User.filter(team_id=team_id))
    # Incase of no members, it just returns an empty list.
    return members

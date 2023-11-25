from __future__ import annotations

from fastapi import APIRouter
from pwncore.models import Team, User, Team_Pydantic, User_Pydantic
from pwncore.routes.auth import RequireJwt

# Metadata at the top for instant accessibility
metadata = {"name": "team", "description": "Operations with teams"}

router = APIRouter(prefix="/team", tags=["team"])


@router.get("/list")
async def team_list():
    teams = await Team_Pydantic.from_queryset(Team.all())
    return teams


# Unable to test as adding users returns an error
@router.get("/members")
async def team_members(jwt: RequireJwt):
    team_id = jwt["team_id"]
    members = await User_Pydantic.from_queryset(User.filter(team_id=team_id))
    # Incase of no members, it just returns an empty list.
    return members

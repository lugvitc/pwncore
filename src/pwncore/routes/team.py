from __future__ import annotations

from fastapi import APIRouter
from pwncore.models import Team, User, Team_Pydantic, User_Pydantic

# Metadata at the top for instant accessibility
metadata = {"name": "team", "description": "Operations with teams"}

router = APIRouter(prefix="/team", tags=["team"])


# Retrieve team_id from cookies
def get_team_id():
    return 1


@router.get("/list")
async def team_list():
    teams = await Team_Pydantic.from_queryset(Team.all())
    return teams


@router.get("/login")
async def team_login():
    # Do login verification here
    return {"status": "logged in!"}


# Unable to test as adding users returns an error
@router.get("/members")
async def team_members():
    members = await User_Pydantic.from_queryset(User.filter(team_id=get_team_id()))
    # Incase of no members, it just returns an empty list.
    return members

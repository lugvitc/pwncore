# Metadata at the top for instant accessibility
metadata = {
    "name": "team",
    "description": "Operations with teams"
}

from fastapi import APIRouter

router = APIRouter(
    prefix="/team",
    tags=["team"]
)


@router.get("/list")
async def team_list():
    # Do login verification here
    return [{"team_name": "CID Squad"}, {"team_name": "Astra"}]


@router.get("/login")
async def team_login():
    # Do login verification here
    return {"status": "logged in!"}


@router.get("/members/{team_id}")
async def team_members(team_id: int):
    # Get team members from team_id
    return [{"name": "ABC", "user_id": 3432}, {"name": "DEF", "user_id": 3422}]

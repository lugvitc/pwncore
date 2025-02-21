from __future__ import annotations

from fastapi import APIRouter, Response
from pydantic import BaseModel
from tortoise.transactions import atomic

from pwncore.config import config
from pwncore.models import Team, User, Team_Pydantic, User_Pydantic, Container
from pwncore.routes.auth import RequireJwt

# from pwncore.routes.leaderboard import gcache

# Metadata at the top for instant accessibility
metadata = {"name": "team", "description": "Operations with teams"}

router = APIRouter(prefix="/team", tags=["team"])


class UserAddBody(BaseModel):
    tag: str
    name: str
    email: str
    phone_num: str


class UserRemoveBody(BaseModel):
    tag: str


@router.get("/list",
    summary="Get all teams",
    description="""Returns a complete list of registered teams.
    
    Example response:
    ```json
    [
        {
            "id": 1,
            "name": "Team Alpha",
            "coins": 100,
            "points": 250
        }
    ]
    ```
    """)
async def team_list():
    teams = await Team_Pydantic.from_queryset(Team.all())
    return teams


# Unable to test as adding users returns an error
@router.get("/members",
    summary="Get team members",
    description="""Returns a list of all members in the authenticated team.
    
    Example response:
    ```json
    [
        {
            "tag": "23BCE1000",
            "name": "John Doe",
            "email": "john@example.com",
            "phone_num": "1234567890"
        }
    ]
    ```
    
    Note: Returns an empty list if no members are found.
    """)
async def team_members(jwt: RequireJwt):
    team_id = jwt["team_id"]
    members = await User_Pydantic.from_queryset(User.filter(team_id=team_id))
    # Incase of no members, it just returns an empty list.
    return members


@router.get("/me",
    summary="Get authenticated team details",
    description="""Returns the details of the currently authenticated team.
    
    Example response:
    ```json
    {
        "id": 1,
        "name": "Team Alpha",
        "coins": 100,
        "points": 250
    }
    ```
    """)
async def get_self_team(jwt: RequireJwt):
    team_id = jwt["team_id"]

    team_model = await Team.get(id=team_id)

    team = dict(await Team_Pydantic.from_tortoise_orm(team_model))
    # Get points from leaderboard
    # would be better is cache stores the values in a dict indexed by team id
    # for leaderboard_team in gcache.data:
    #     if leaderboard_team["name"] == team["name"]:
    #         team["tpoints"] = leaderboard_team["tpoints"]
    #         break

    return team


@atomic()
@router.post("/add",
    summary="Add member to team",
    description="""Add a new member to the authenticated team.
    
    Example request:
    ```json
    {
        "tag": "23BCE1000",
        "name": "John Doe",
        "email": "john@example.com",
        "phone_num": "1234567890"
    }
    ```
    
    Example response:
    ```json
    {
        "msg_code": 18
    }
    ```
    
    Note: Returns error 403 if user already exists in a team.
    """)
async def add_member(user: UserAddBody, response: Response, jwt: RequireJwt):
    team_id = jwt["team_id"]

    if await User.get_or_none(tag=user.tag):
        response.status_code = 403
        return {"msg_code": config.msg_codes["user_already_in_team"]}

    try:
        await User.create(
            # Validation for user tag (reg. no. in our case)
            # needs to be done on frontend to not make the server event specific
            tag=user.tag.strip().casefold(),
            name=user.name,
            email=user.email,
            phone_num=user.phone_num,
            team_id=team_id,
        )
    except Exception:
        response.status_code = 500
        return {"msg_code": config.msg_codes["db_error"]}
    return {"msg_code": config.msg_codes["user_added"]}


@atomic()
@router.post("/remove",
    summary="Remove member from team",
    description="""Remove an existing member from the authenticated team.
    
    Example request:
    ```json
    {
        "tag": "23BCE1000"
    }
    ```
    
    Example response:
    ```json
    {
        "msg_code": 19
    }
    ```
    
    Note: Returns error 403 if user is not found in team.
    """)
async def remove_member(user_info: UserRemoveBody, response: Response, jwt: RequireJwt):
    team_id = jwt["team_id"]

    user = await User.get_or_none(team_id=team_id, tag=user_info.tag)
    if not user:
        response.status_code = 403
        return {"msg_code": config.msg_codes["user_not_in_team"]}

    try:
        await user.delete()
    except Exception:
        response.status_code = 500
        return {"msg_code": config.msg_codes["db_error"]}
    return {"msg_code": config.msg_codes["user_removed"]}


@router.get("/containers",
    summary="Get team containers",
    description="""Get all containers associated with the authenticated team.
    
    Example response:
    ```json
    {
        "1": [8080, 22],
        "2": [8081]
    }
    ```
    
    Note: Object keys are problem IDs and values are lists of exposed ports.
    """)
async def get_team_containers(response: Response, jwt: RequireJwt):
    containers = await Container.filter(team_id=jwt["team_id"]).prefetch_related(
        "ports", "problem"
    )

    result = {}
    for container in containers:
        # mypy complains id doesnt exist in Problem
        result[container.problem.id] = await container.ports.all().values_list(  # type: ignore[attr-defined]
            "port", flat=True
        )

    return result

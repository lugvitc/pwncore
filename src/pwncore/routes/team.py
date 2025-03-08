from __future__ import annotations

from fastapi import APIRouter, Response
from tortoise.transactions import atomic

from pwncore.config import config

from pwncore.models import Team, User, Team_Pydantic, User_Pydantic, Container

from pwncore.models.responseModels.ctf_ContainerStatusResponse import ContainerPortsResponse
from pwncore.models.responseModels.user_mgmtResponse import UserAddBody, UserRemoveBody, MessageResponse

from pwncore.routes.auth import RequireJwt


# from pwncore.routes.leaderboard import gcache

# Metadata at the top for instant accessibility
metadata = {"name": "team", "description": "Operations with teams"}

router = APIRouter(prefix="/team", tags=["team"])

     
@router.get("/list",
    response_model=list[Team_Pydantic],
    response_description="""Returns a complete list of registered teams.
    
    Response Parameters: `id`, `name`, `coins`, `points`

    """)
async def team_list():
    teams = await Team_Pydantic.from_queryset(Team.all())
    return teams


# Unable to test as adding users returns an error
     
@router.get("/members",
    response_model=list[User_Pydantic],
    response_description="""Returns a list of all members in the authenticated team.
    
    Response Parameters: `tag`, `name`, `email`, `phone_num`
    
    Note: Returns an empty list if no members are found.
    """)
async def team_members(jwt: RequireJwt):
    team_id = jwt["team_id"]
    members = await User_Pydantic.from_queryset(User.filter(team_id=team_id))
    # Incase of no members, it just returns an empty list.
    return members

     
@router.get("/me",
    response_model=Team_Pydantic,
    response_description="""Returns the details of the currently authenticated team.
    
    Response Parameters: `id`, `name`, `coins`, `points`

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
    response_model=MessageResponse,
    response_description="""Add a new member to the authenticated team.
    
    Request Parameters: `tag`, `name`, `email`, `phone_num`
    
    msg_code for response:
    - (success) user_added: 18
    - (fail) 
        - user_already_in_team: 20
        - db_error: 0
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
    response_model=MessageResponse,
    response_description="""Remove an existing member from the authenticated team.
    
    Parameters:
        - for request: `tag`
        - for response: `msg_code`

    Msg_code for response:
    - (success) user_removed: 19
    - (fail)
        - user_not_in_team : 21
        - db_error: 0
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
    response_model=ContainerPortsResponse,
    response_description="""Get all containers associated with the authenticated team.
    
    Note: Object keys are problem IDs and values are lists of the containers' exposed ports.
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

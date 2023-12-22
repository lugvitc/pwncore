from __future__ import annotations

from fastapi import APIRouter, Response
from pydantic import BaseModel
from tortoise.transactions import atomic

from pwncore.config import config
from pwncore.models import Team, User, Team_Pydantic, User_Pydantic
from pwncore.routes.auth import RequireJwt

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


@atomic()
@router.post("/add")
async def add_member(user: UserAddBody, response: Response, jwt: RequireJwt):
    team_id = jwt["team_id"]

    if await User.get_or_none(tag=user.tag):
        response.status_code = 403
        return {"msg_code": config.msg_codes["user_already_in_team"]}

    try:
        await User.create(
            # Validation for user tag (reg. no. in our case)
            # needs to be done on frontend to not make the server event specific
            tag=user.tag,
            name=user.name,
            email=user.email,
            phone_num=user.phone_num,
            team_id=team_id
        )
    except Exception:
        response.status_code = 500
        return {"msg_code": config.msg_codes["db_error"]}
    return {"msg_code": config.msg_codes["user_added"]}


@atomic()
@router.post("/remove")
async def add_member(user_info: UserRemoveBody, response: Response, jwt: RequireJwt):
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

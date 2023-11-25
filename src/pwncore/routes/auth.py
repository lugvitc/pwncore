from __future__ import annotations

import datetime
import typing as t

import jwt
from fastapi import APIRouter, Header, Response, HTTPException, Depends
from passlib.hash import bcrypt
from pydantic import BaseModel
from tortoise.transactions import atomic

from pwncore.models import Team
from pwncore.config import config

# Metadata at the top for instant accessibility
metadata = {
    "name": "auth",
    "description": "Authentication using a JWT using a single access token.",
}

router = APIRouter(prefix="/auth", tags=["auth"])


class SignupBody(BaseModel):
    name: str
    password: str
    # members: list[str]


class LoginBody(BaseModel):
    name: str
    password: str


@atomic()
@router.post("/signup")
async def signup_team(team: SignupBody, response: Response):
    try:
        if await Team.exists(name=team.name):
            response.status_code = 406
            return {"msg_code": config.msg_codes["team_exists"]}

        # TODO: Add users details

        await Team.create(name=team.name, secret_hash=bcrypt.hash(team.password))
    except Exception:
        response.status_code = 500
        return {"msg_code": config.msg_codes["db_error"]}
    return {"msg_code": config.msg_codes["signup_success"]}


@router.post("/login")
async def team_login(team_data: LoginBody, response: Response):
    # TODO: Simplified logic since we're not doing refresh tokens.

    team = await Team.get_or_none(name=team_data.name)
    if team is None:
        response.status_code = 404
        return {"msg_code": config.msg_codes["team_not_found"]}
    if not bcrypt.verify(team_data.password, team.secret_hash):
        response.status_code = 401
        return {"msg_code": config.msg_codes["wrong_password"]}

    current_time = datetime.datetime.utcnow()
    expiration_time = current_time + datetime.timedelta(hours=config.jwt_valid_duration)
    token_payload = {"team_id": team.id, "exp": expiration_time}
    token = jwt.encode(token_payload, config.jwt_secret, algorithm="HS256")

    # Returning token to be sent as an authorization header "Bearer <TOKEN>"
    return {
        "msg_code": config.msg_codes["login_success"],
        "access_token": token,
        "token_type": "bearer",
    }


# Custom JWT processing (since FastAPI's implentation deals with refresh tokens)
# Supressing B008 in order to be able to use Header() in arguments
def get_jwt(*, authorization: t.Annotated[str, Header()]) -> JwtInfo:  # noqa: B008
    try:
        token = authorization.split(" ")[1]  # Remove Bearer
        decoded_token: JwtInfo = jwt.decode(
            token, config.jwt_secret, algorithms=["HS256"]
        )
    except Exception:  # Will filter for invalid signature/expired tokens
        raise HTTPException(status_code=401)
    return decoded_token


# Using a pre-assigned variable everywhere else to follow flake8's B008
JwtInfo = t.TypedDict("JwtInfo", {"team_id": int, "exp": int})
RequireJwt = t.Annotated[JwtInfo, Depends(get_jwt)]

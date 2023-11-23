from __future__ import annotations

import jwt
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from tortoise.contrib.pydantic import pydantic_model_creator
from pwncore.models import User, Team
from pwncore.config import config
import datetime
from passlib.hash import bcrypt

# Metadata at the top for instant accessibility
metadata = {"name": "team", "description": "Operations with teams"}

router = APIRouter(prefix="/team", tags=["team"])

Team_pydantic = pydantic_model_creator(Team, name='Team')
TeamIn_pydantic = pydantic_model_creator(Team, name='TeamIn', exclude_readonly=True)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')


async def get_current_team(token : str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, config.jwt_secret, algorithms=['HS256'])
        team = await Team.get(id=payload.get('id'))
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid team name or password"
        )
    return await Team_pydantic.from_tortoise_orm(team)


async def generate_token(team_data : TeamIn_pydantic):
    team = await Team.get_or_none(name=team_data.name)
    if team is not None and await team.check_password(team_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid team name or password"
        )

    team_obj = await Team_pydantic.from_tortoise_orm(team)
    expiration_time = datetime.datetime.utcnow() + datetime.timedelta(hours=2)
    payload = team_obj.dict()
    payload['exp'] = expiration_time
    token = jwt.encode(payload, config.jwt_secret, algorithm='HS256')

    return {
        "access_token" : token,
        "token_type" : "bearer",
        "expires_at" : expiration_time
    }


@router.post('/signup', response_model=Team_pydantic)
async def signup_team(team : TeamIn_pydantic):
    team_obj = await Team.create(
        name=team.name,
        password=bcrypt.hash(team.password)
    )
    return await Team_pydantic.from_tortoise_orm(team_obj)


@router.post('/login')
async def team_login(
    team_data : TeamIn_pydantic,
    token : str = Depends(oauth2_scheme),
    team : Team_pydantic = Depends(get_current_team)
):

    if team_data.name in (jwt.decode(token, config.jwt_secret, algorithms=['HS256'])):
        issued_at = datetime.datetime.utcfromtimestamp(token['iat'])
        current_time = datetime.datetime.utcnow()
        idle_time = current_time - issued_at

        if idle_time < datetime.timedelta(hours=2):
            expiration_time = current_time + datetime.timedelta(hours=2)
            token_payload = jwt.decode(token, config.jwt_secret, algorithms=['HS256'])
            token_payload['exp'] = expiration_time
            token = jwt.encode(token_payload, config.jwt_secret, algorithm='HS256')

        return {
            "access_token": token,
            "token_type": "bearer"
        }
    else:
        return generate_token(team_data)

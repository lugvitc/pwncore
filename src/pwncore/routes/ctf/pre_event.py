from __future__ import annotations

from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, Response
from pydantic import BaseModel
from tortoise.transactions import atomic
from tortoise.functions import Sum
from tortoise.exceptions import DoesNotExist, IntegrityError

from pwncore.models import (
    PreEventProblem,
    PreEventSolvedProblem,
    PreEventUser,
    PreEventProblem_Pydantic,
)
from pwncore.config import config

router = APIRouter(prefix="/pre", tags=["ctf"])
_IST = timezone(timedelta(hours=5, minutes=30))


class PreEventFlag(BaseModel):
    tag: str
    flag: str
    email: str


class CoinsQuery(BaseModel):
    tag: str


@router.get("/list")
async def ctf_list():
    problems = await PreEventProblem_Pydantic.from_queryset(PreEventProblem.all())
    return problems


@router.get("/today")
async def ctf_today():
    return await PreEventProblem_Pydantic.from_queryset(
        PreEventProblem().filter(date=datetime.now(_IST).date())
    )


@router.get("/coins/{tag}")
async def coins_get(tag: str):
    try:
        return {
            "coins": await PreEventUser.get(tag=tag.strip().casefold())
            .annotate(coins=Sum("solvedproblems__problem__points"))
            .values_list("coins", flat=True)
        }
    except DoesNotExist:
        return 0


@atomic()
@router.post("/{ctf_id}/flag")
async def pre_event_flag_post(ctf_id: int, post_body: PreEventFlag, response: Response):
    problem = await PreEventProblem.get_or_none(id=ctf_id)

    if not problem or (problem.date != datetime.now(_IST).date()):
        response.status_code = 404
        return {"msg_code": config.msg_codes["ctf_not_found"]}

    user_tag = post_body.tag.strip().casefold()

    if await PreEventSolvedProblem.exists(user_id=user_tag, problem_id=ctf_id):
        response.status_code = 401
        return {"msg_code": config.msg_codes["ctf_solved"]}

    try:
        pu = await PreEventUser.get_or_none(tag=user_tag)
        print(pu, user_tag, post_body.email)
        if pu is None:
            print(1)
            pu = await PreEventUser.create(tag=user_tag, email=post_body.email)
        elif pu.email != post_body.email:
            print(2)
            pu.email = post_body.email
            await pu.save()
    except IntegrityError:
        response.status_code = 401
        return {"msg_code": config.msg_codes["user_or_email_exists"]}

    if status := problem.flag == post_body.flag:
        await PreEventSolvedProblem.create(user=pu, problem_id=ctf_id)

    coins = (
        await PreEventUser.get(tag=user_tag)
        .annotate(coins=Sum("solvedproblems__problem__points"))
        .values_list("coins", flat=True)
    )

    return {"status": status, "coins": coins}


@router.get("/{ctf_id}")
async def ctf_get(ctf_id: int, response: Response):
    problem = await PreEventProblem_Pydantic.from_queryset(
        PreEventProblem.filter(id=ctf_id)
    )
    if not problem:
        response.status_code = 404
        return {"msg_code": config.msg_codes["ctf_not_found"]}
    return problem

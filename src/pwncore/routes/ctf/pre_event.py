from __future__ import annotations

from datetime import datetime, timezone, timedelta

from typing import Union

from fastapi import APIRouter, Response
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

from pwncore.models.responseModels.preEventCTF_response import (
    CoinsResponse,
    FlagSubmissionResponse,
    preEventCTF_ErrorResponse as ErrorResponse,
    PreEventFlag,
    CoinsQuery
)   

router = APIRouter(prefix="/pre", tags=["ctf"])
_IST = timezone(timedelta(hours=5, minutes=30))


     
@router.get(
    "/list",
    response_model=list[PreEventProblem_Pydantic],
    response_description="""Returns a list of all available pre-event CTF problems.
    Flag field is excluded from response for security.
    """)
async def ctf_list():
    problems = await PreEventProblem_Pydantic.from_queryset(PreEventProblem.all())
    return problems

     
@router.get(
    "/today",
    response_model=list[PreEventProblem_Pydantic],
    response_description="""Returns list of CTF problems scheduled for current date.
    Returns empty list if no problems are scheduled for today.
    """)
async def ctf_today():
    return await PreEventProblem_Pydantic.from_queryset(
        PreEventProblem().filter(date=datetime.now(_IST).date())
    )

     
@router.get(
    "/coins/{tag}",
    response_model=CoinsResponse,
    response_description="""Get total coins earned by a user in pre-event CTFs.
    
    Note: Returns msg_code : 11 if user_not_found.
    """)
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
@router.post(
    "/{ctf_id}/flag",
    response_model=Union[FlagSubmissionResponse, ErrorResponse],
    response_description="""Submit a solution flag for a pre-event CTF problem.

    Msg_codes for Error responses:
    - 404: if ctf_not_found or not for current date: 2
    - 401: if ctf_solved already: 12
    - 401: (exception) if user_or_email_exists : 23
    """)

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

          
@router.get(
    "/{ctf_id}",
    response_model=Union[list[PreEventProblem_Pydantic], ErrorResponse],
    response_description="""Get complete details of a specific pre-event CTF problem.
    
    msg_code for Error response:
    - if ctf_not_found : 2
    """)
async def ctf_get(ctf_id: int, response: Response):
    problem = await PreEventProblem_Pydantic.from_queryset(
        PreEventProblem.filter(id=ctf_id)
    )
    if not problem:
        response.status_code = 404
        return {"msg_code": config.msg_codes["ctf_not_found"]}
    return problem

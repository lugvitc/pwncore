from __future__ import annotations

from fastapi import APIRouter, Response
from pydantic import BaseModel
from tortoise.transactions import atomic

from pwncore.models import (
    PreEventProblem,
    PreEventSolvedProblem,
    BaseProblem_Pydantic,
)
from pwncore.config import config

router = APIRouter(prefix="/pre", tags=["ctf"])


class PreEventFlag(BaseModel):
    tag: str
    flag: str


@router.get("/list")
async def ctf_list():
    problems = await BaseProblem_Pydantic.from_queryset(PreEventProblem.all())
    return problems


@atomic()
@router.post("/{ctf_id}/flag")
async def pre_event_flag_post(ctf_id: int, post_body: PreEventFlag, response: Response):
    problem = await PreEventProblem.get_or_none(id=ctf_id)
    if not problem:
        response.status_code = 404
        return {"msg_code": config.msg_codes["ctf_not_found"]}

    user_tag = post_body.tag.strip().casefold()

    if await PreEventSolvedProblem.exists(tag=user_tag, problem_id=ctf_id):
        response.status_code = 401
        return {"msg_code": config.msg_codes["ctf_solved"]}

    if problem.flag == post_body.flag:
        await PreEventSolvedProblem.create(tag=user_tag, problem_id=ctf_id)

        return {"status": True}
    return {"status": False}


@router.get("/{ctf_id}")
async def ctf_get(ctf_id: int, response: Response):
    problem = await BaseProblem_Pydantic.from_queryset(
        PreEventProblem.filter(id=ctf_id)
    )
    if not problem:
        response.status_code = 404
        return {"msg_code": config.msg_codes["ctf_not_found"]}
    return problem

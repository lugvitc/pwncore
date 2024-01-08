from __future__ import annotations

from fastapi import APIRouter, Response
from pydantic import BaseModel
from tortoise.transactions import atomic

from pwncore.models import (
    Problem,
    SolvedProblem,
    Container,
    Hint,
    ViewedHint,
    Problem_Pydantic,
    Hint_Pydantic,
    Team,
    PreEventSolvedProblem,
)
from pwncore.config import config
from pwncore.routes.ctf.start import router as start_router
from pwncore.routes.auth import RequireJwt

# Metadata at the top for instant accessibility
metadata = {
    "name": "ctf",
    "description": "Operations related to CTF, except"
    "create and delete (those are under admin)",
}

router = APIRouter(prefix="/ctf", tags=["ctf"])
router.include_router(start_router)


class Flag(BaseModel):
    flag: str


class PreEventFlag(BaseModel):
    tag: str
    flag: str


@router.get("/list")
async def ctf_list():
    problems = await Problem_Pydantic.from_queryset(Problem.all())
    return problems


@atomic()
@router.post("/{ctf_id}/flag")
async def flag_post(ctf_id: int, flag: Flag, response: Response, jwt: RequireJwt):
    team_id = jwt["team_id"]
    problem = await Problem.get_or_none(id=ctf_id)
    if not problem:
        response.status_code = 404
        return {"msg_code": config.msg_codes["ctf_not_found"]}

    status = await SolvedProblem.exists(team_id=team_id, problem_id=ctf_id)
    if status:
        response.status_code = 401
        return {"msg_code": config.msg_codes["ctf_solved"]}

    check_solved = await Container.exists(
        team_id=team_id, flag=flag.flag, problem_id=ctf_id
    )
    if check_solved:
        await SolvedProblem.create(team_id=team_id, problem_id=ctf_id)

        team = await Team.get(id=team_id)
        team.coins += problem.coins
        await team.save()

        return {"status": True}
    return {"status": False}


@atomic()
@router.post("/{ctf_id}/pre_event_flag")
async def pre_event_flag_post(ctf_id: int, post_body: PreEventFlag, response: Response):
    problem = await Problem.get_or_none(id=ctf_id)
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


@atomic()
@router.get("/{ctf_id}/hint")
async def hint_get(ctf_id: int, response: Response, jwt: RequireJwt):
    team_id = jwt["team_id"]
    problem = await Problem.exists(id=ctf_id)
    if not problem:
        response.status_code = 404
        return {"msg_code": config.msg_codes["ctf_not_found"]}

    team = await Team.get(id=team_id)
    if team.coins < config.hint_penalty:
        return {"msg_code": config.msg_codes["insufficient_coins"]}

    viewed_hints = (
        await Hint.filter(problem_id=ctf_id, viewedhints__team_id=team_id)
        .order_by("-order")
        .first()
    )
    if viewed_hints:
        if not await Hint.exists(problem_id=ctf_id, order=viewed_hints.order + 1):
            response.status_code = 403
            return {"msg_code": config.msg_codes["hint_limit_reached"]}

        hint = await Hint.get(problem_id=ctf_id, order=viewed_hints.order + 1)

    else:
        hint = await Hint.get(problem_id=ctf_id, order=0)

    team.coins -= config.hint_penalty
    await team.save()

    await ViewedHint.create(hint_id=hint.id, team_id=team_id)
    return {"text": hint.text, "order": hint.order}


@router.get("/{ctf_id}/viewed_hints")
async def viewed_problem_hints_get(ctf_id: int, jwt: RequireJwt):
    team_id = jwt["team_id"]
    viewed_hints = await Hint_Pydantic.from_queryset(
        Hint.filter(problem_id=ctf_id, viewedhints__team_id=team_id)
    )
    return viewed_hints


@router.get("/completed")
async def completed_problem_get(jwt: RequireJwt):
    team_id = jwt["team_id"]
    problems = await Problem_Pydantic.from_queryset(
        Problem.filter(solvedproblems__team_id=team_id)
    )
    return problems


@router.get("/{ctf_id}")
async def ctf_get(ctf_id: int, response: Response):
    problem = await Problem_Pydantic.from_queryset(Problem.filter(id=ctf_id))
    if not problem:
        response.status_code = 404
        return {"msg_code": config.msg_codes["ctf_not_found"]}
    return problem

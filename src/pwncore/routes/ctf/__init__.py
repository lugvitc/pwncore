from __future__ import annotations

from fastapi import APIRouter
from fastapi import Response

from pwncore.models import (
    Problem,
    SolvedProblem,
    Container,
    Hint,
    ViewedHint,
    Problem_Pydantic,
    Hint_Pydantic,
)
from pwncore.config import config
from pwncore.routes.team import get_team_id

# Metadata at the top for instant accessibility
metadata = {
    "name": "ctf",
    "description": "Operations related to CTF, except"
    "create and delete (those are under admin)",
}

router = APIRouter(prefix="/ctf", tags=["ctf"])

# Routes that do not need a separate submodule for themselves


# For testing purposes. Replace function with POST method
def get_flag():
    return "pwncore{flag_1}"


@router.get("/list")
async def ctf_list():
    problems = await Problem_Pydantic.from_queryset(Problem.all())
    return problems


# For testing purposes only. flag to be passed in body of POST function.
@router.get("/{ctf_id}/flag")
async def flag_get(ctf_id: int, response: Response):
    problem = await Problem.exists(id=ctf_id)
    if not problem:
        response.status_code = 404
        return {"msg_code": config.msg_codes["ctf_not_found"]}

    status = await SolvedProblem.get_or_none(team_id=get_team_id(), problem_id=ctf_id)
    if status:
        response.status_code = 401
        return {"msg_code": config.msg_codes["ctf_solved"]}

    check_solved = await Container.get_or_none(
        team_id=get_team_id(), flag=get_flag(), problem_id=ctf_id
    )
    if check_solved:
        await SolvedProblem.create(team_id=get_team_id(), problem_id=ctf_id)
        return {"status": True}
    return {"status": False}


@router.get("/{ctf_id}/hint")
async def hint_get(ctf_id: int, response: Response):
    problem = await Problem.exists(id=ctf_id)
    if not problem:
        response.status_code = 404
        return {"msg_code": config.msg_codes["ctf_not_found"]}

    viewed_hints = await Hint_Pydantic.from_queryset(
        Hint.filter(problem_id=ctf_id, hint__team_id=get_team_id()).prefetch_related(
            "hint"
        )
    )

    if viewed_hints:
        hint = await Hint.exists(problem_id=ctf_id, order=viewed_hints[-1].order + 1)
        if not hint:
            response.status_code = 403
            return {"msg_code": config.msg_codes["hint_limit_reached"]}

        hint = await Hint_Pydantic.from_queryset_single(
            Hint.get(problem_id=ctf_id, order=viewed_hints[-1].order + 1)
        )

    else:
        hint = await Hint_Pydantic.from_queryset_single(
            Hint.get(problem_id=ctf_id, order=0)
        )

    await ViewedHint.create(hint_id=hint.id, team_id=get_team_id())
    return hint


@router.get("/viewed_hints")
async def viewed_hints_get():
    viewed_hints = await Hint_Pydantic.from_queryset(
        Hint.filter(hint__team_id=get_team_id()).prefetch_related("hint")
    )
    return viewed_hints


@router.get("/{ctf_id}/viewed_hints")
async def viewed_problem_hints_get(ctf_id: int):
    viewed_hints = await Hint_Pydantic.from_queryset(
        Hint.filter(problem_id=ctf_id, hint__team_id=get_team_id()).prefetch_related(
            "hint"
        )
    )
    return viewed_hints


@router.get("/completed")
async def completed_problem_get():
    problems = await Problem_Pydantic.from_queryset(
        Problem.filter(problem__team_id=get_team_id()).prefetch_related("problem")
    )
    return problems


@router.get("/{ctf_id}")
async def ctf_get(ctf_id: int, response: Response):
    problem = await Problem_Pydantic.from_queryset(Problem.filter(id=ctf_id))
    if not problem:
        response.status_code = 404
        return {"msg_code": config.msg_codes["ctf_not_found"]}
    return problem

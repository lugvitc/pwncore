from __future__ import annotations

from asyncio import create_task
from collections import defaultdict
from logging import getLogger

from fastapi import APIRouter, Request, Response
from pydantic import BaseModel
from tortoise.transactions import atomic

import pwncore.containerASD as containerASD
from pwncore.config import config
from pwncore.models import (
    Container,
    Hint,
    Hint_Pydantic,
    Problem,
    SolvedProblem,
    Team,
    ViewedHint,
)
from pwncore.models.ctf import Problem_Pydantic
from pwncore.routes.auth import RequireJwt
from pwncore.routes.ctf.pre_event import router as pre_event_router
from pwncore.routes.ctf.start import router as start_router

# Metadata at the top for instant accessibility
metadata = {
    "name": "ctf",
    "description": "Operations related to CTF, except"
    "create and delete (those are under admin)",
}

router = APIRouter(prefix="/ctf", tags=["ctf"])
router.include_router(start_router)
router.include_router(pre_event_router)

logger = getLogger("routes.ctf")


def _invalid_order():
    logger.warn("= Invalid penalty lookup by order occured =")
    return 0


# 0 - 10 - 10
# 1 - 5  - 15
# 2 - 10 - 25
HINTPENALTY = defaultdict(_invalid_order, {0: 10, 1: 5, 2: 10})


class Flag(BaseModel):
    flag: str


@router.get("/completed")
async def completed_problem_get(jwt: RequireJwt):
    team_id = jwt["team_id"]
    ViewedHint.filter(team_id=team_id).annotate()
    problems = await Problem_Pydantic.from_queryset(
        Problem.filter(solvedproblems__team_id=team_id, visible=True)
    )
    return problems


@router.get("/list")
async def ctf_list(jwt: RequireJwt):
    team_id = jwt["team_id"]
    problems = await Problem_Pydantic.from_queryset(Problem.filter(visible=True))
    acc: dict[int, float] = defaultdict(lambda: 1.0)
    for k, v in map(
        lambda x: (x.hint.problem_id, HINTPENALTY[x.hint.order]),  # type: ignore[attr-defined]
        await ViewedHint.filter(team_id=team_id, with_points=True).prefetch_related(
            "hint"
        ),
    ):
        acc[k] -= v / 100
    for i in problems:
        i.points = int(acc[i.id] * i.points)  # type: ignore[attr-defined]
    return problems


async def update_points(req: Request, ctf_id: int):
    try:
        p = await Problem.get(id=ctf_id)
        await p.update_points()
        req.app.state.force_expire = True
    except Exception:
        logger.exception("An error occured while updating points")


@atomic()
@router.post("/{ctf_id}/flag")
async def flag_post(
    req: Request, ctf_id: int, flag: Flag, response: Response, jwt: RequireJwt
):
    team_id = jwt["team_id"]
    problem = await Problem.get_or_none(id=ctf_id, visible=True)
    if not problem:
        response.status_code = 404
        return {"msg_code": config.msg_codes["ctf_not_found"]}

    status = await SolvedProblem.exists(team_id=team_id, problem_id=ctf_id)
    if status:
        response.status_code = 401
        return {"msg_code": config.msg_codes["ctf_solved"]}

    team_container = await Container.get_or_none(team_id=team_id, problem_id=ctf_id)
    if not team_container:
        return {"msg_code": config.msg_codes["container_not_found"]}

    if team_container.flag == flag.flag.strip():
        hints = await Hint.filter(
            problem_id=ctf_id,
            viewedhints__team_id=team_id,
            viewedhints__with_points=True,
        )
        pnlt = (100 - sum(map(lambda h: HINTPENALTY[h.order], hints))) / 100

        # Stop container after submitting
        try:
            await Container.filter(team_id=team_id, problem_id=ctf_id).delete()
        except Exception:
            response.status_code = 500
            return {"msg_code": config.msg_codes["db_error"]}

        container = await containerASD.docker_client.containers.get(
            team_container.docker_id
        )
        await container.kill()
        await container.delete()
        #

        await SolvedProblem.create(team_id=team_id, problem_id=ctf_id, penalty=pnlt)
        create_task(update_points(req, ctf_id))
        return {"status": True}
    return {"status": False}


@atomic()
@router.get("/{ctf_id}/hint")
async def hint_get(ctf_id: int, response: Response, jwt: RequireJwt):
    team_id = jwt["team_id"]
    problem = await Problem.exists(id=ctf_id, visible=True)
    if not problem:
        response.status_code = 404
        return {"msg_code": config.msg_codes["ctf_not_found"]}

    team = await Team.get(id=team_id)
    # if team.coins < config.hint_penalty:
    #     return {"msg_code": config.msg_codes["insufficient_coins"]}

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

    with_points = team.coins < config.hint_penalty
    if not with_points:
        team.coins -= config.hint_penalty
        await team.save()

    await ViewedHint.create(hint_id=hint.id, team_id=team_id, with_points=with_points)
    return {
        "text": hint.text,
        "order": hint.order,
    }


@router.get("/{ctf_id}/viewed_hints")
async def viewed_problem_hints_get(ctf_id: int, jwt: RequireJwt):
    team_id = jwt["team_id"]
    viewed_hints = await Hint_Pydantic.from_queryset(
        Hint.filter(problem_id=ctf_id, viewedhints__team_id=team_id)
    )
    return viewed_hints


@router.get("/{ctf_id}")
async def ctf_get(ctf_id: int, response: Response):
    problem = await Problem_Pydantic.from_queryset(
        Problem.filter(id=ctf_id, visible=True)
    )
    if not problem:
        response.status_code = 404
        return {"msg_code": config.msg_codes["ctf_not_found"]}
    return problem

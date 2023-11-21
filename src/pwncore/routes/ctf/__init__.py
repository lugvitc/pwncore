from fastapi import APIRouter
from fastapi import Response

from pwncore.routes.ctf.start import router as start_router
from pwncore.models.ctf import Problem
from pwncore.models import Problem, SolvedProblem, Container, Hint, ViewedHint
from pwncore.config import config
import uuid

# Metadata at the top for instant accessibility
metadata = {
    "name": "ctf",
    "description": "Operations related to CTF, except"
    "create and delete (those are under admin)",
}

router = APIRouter(prefix="/ctf", tags=["ctf"])
router.include_router(start_router)

# Routes that do not need a separate submodule for themselves
# Fetch team_id from cookies
def get_team_id():
    return 1


@router.get("/list")
async def ctf_list(response: Response):
    problems = await Problem_Pydantic.from_queryset(Problem.all())
    return problems


# For testing purposes only. flag to be passed in body of POST function.
@router.get("/{ctf_id}/flag/{flag}")
async def flag_get(ctf_id: int, flag: str, response: Response):
    problem = await Problem.exists(id=ctf_id)
    if not problem:
        response.status_code = 404
        return {"msg_code": config.msg_codes["ctf_not_found"]}

    status = await SolvedProblem.get_or_none(team_id=get_team_id(), problem_id=ctf_id)
    if status:
        response.status_code = 401
        return {"msg_code": config.msg_codes["ctf_solved"]}

    check_solved = await Container.get_or_none(
        team_id=get_team_id(), flag=flag, problem_id=ctf_id
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

    viewed = await ViewedHint.filter(team_id=get_team_id()).values_list(
        "hint_id", flat=True
    )

    if viewed:
        viewed_hint = await Hint.filter(problem_id=ctf_id, id__in=viewed).values_list(
            "order", flat=True
        )
        if viewed_hint:
            hint = await Hint.get_or_none(
                problem_id=ctf_id, order=max(viewed_hint) + 1  # type: ignore[operator]
            ).values()
        else:
            hint = await Hint.get(problem_id=ctf_id, order=0).values()
    else:
        hint = await Hint.get(problem_id=ctf_id, order=0).values()

    if not hint:
        response.status_code = 403
        return {"msg_code": config.msg_codes["hint_limit_reached"]}

    await ViewedHint.create(hint_id=hint["id"], team_id=get_team_id())
    return hint


@router.get("/{ctf_id}/viewed_hints")
async def completed_hints_get(ctf_id: int):
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

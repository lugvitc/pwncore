from __future__ import annotations

from fastapi import APIRouter
from fastapi import Response

from pwncore.models import Problem, SolvedProblem, Container, Hint, ViewedHint, Team
from pwncore.config import config
import uuid

# Metadata at the top for instant accessibility
metadata = {
    "name": "ctf",
    "description": "Operations related to CTF, except"
    "create and delete (those are under admin)",
}

router = APIRouter(prefix="/ctf", tags=["ctf"])

# Routes that do not need a separate submodule for themselves


# Fetch team_id from cookies
def get_team_id():
    return 1


@router.get("/create")
async def init_db():
    if config.development:
        await Problem.create(
            name="Invisible-Incursion",
            description="Chod de tujhe se na ho paye",
            author="Meetesh Saini",
            points=300,
            image_name="key:latest",
            image_config={"PortBindings": {"22/tcp": [{}]}},
        )
        await Problem.create(
            name="In-Plain-Sight",
            description="A curious image with hidden secrets?",
            author="KreativeThinker",
            points=300,
            image_name="key:latest",
            image_config={"PortBindings": {"22/tcp": [{}]}},
        )
        await Team.create(
            name="CID Squad" + uuid.uuid4().hex, secret_hash="veryverysecret"
        )
        await Team.create(
            name="Triple A battery" + uuid.uuid4().hex, secret_hash="chotiwali"
        )
        await Container.create(
            docker_id="letsjustsay1",
            flag="pwncore{this_is_a_test_flag}",
            problem_id=1,
            team_id=1,
        )
        await Container.create(
            docker_id="letsjustsay2",
            flag="pwncore{this_is_a_test_flag}",
            problem_id=2,
            team_id=1,
        )
        await Container.create(
            docker_id="letsjustsay3",
            flag="pwncore{farmers}",
            problem_id=2,
            team_id=2,
        )
        await Hint.create(order=0, problem_id=1, text="This is the first hint")
        await Hint.create(order=1, problem_id=1, text="This is the second hint")
        await Hint.create(order=2, problem_id=1, text="This is the third hint")
        await Hint.create(order=0, problem_id=2, text="This is the first hint")
        await Hint.create(order=1, problem_id=2, text="This is the second hint")


response = Response()


@router.get("/list")
async def ctf_list():
    # Get list of ctfs
    problems = await Problem.all().values()
    if not problems:
        response.status_code = 404
        return {"msg_code": config.msg_codes["ctf_not_found"]}
    return problems


# @router.get("/flag/{ctf_id}")
# async def flag_get(ctf_id: int):
#     flag = await Container.filter(
#         problem_id=ctf_id, team_id=get_team_id(), flag=flag
#     ).values()
#     return flag


# For testing purposes only. flag to be passed in body of POST function.
@router.get("/flag/{ctf_id}/{flag}")
async def flag_get(ctf_id: int, flag: str):
    problem = await Problem.get_or_none(id=ctf_id)
    if not problem:
        response.status_code = 404
        return {"msg_code": config.msg_codes["ctf_not_found"]}

    status = await Container.get_or_none(
        team_id=get_team_id(), flag=flag, problem_id=ctf_id
    )
    if status:
        await SolvedProblem.get_or_create(team_id=get_team_id(), problem_id=ctf_id)
        return {"status": True}
    return {"status": False}


@router.get("/hint/{ctf_id}")
async def hint_get(ctf_id: int):
    problem = await Problem.get_or_none(id=ctf_id)
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


# @router.get("/completed/hint")
@router.get("/viewed_hints")
async def completed_hints_get():
    hints = await ViewedHint.filter(team_id=get_team_id()).values_list(
        "hint_id", flat=True
    )
    viewed_hints = [await Hint.get(id=x) for x in hints]
    return viewed_hints


@router.get("/completed")
async def completed_problem_get():
    problems = await SolvedProblem.filter(team_id=get_team_id()).values_list(
        "problem_id", flat=True
    )
    solved_problems = [await Problem.get(id=x) for x in problems]
    return solved_problems


@router.get("/{ctf_id}")
async def ctf_get(ctf_id: int):
    problem = await Problem.get_or_none(id=ctf_id)
    if not problem:
        response.status_code = 404
        return {"msg_code": config.msg_codes["ctf_not_found"]}

    return problem

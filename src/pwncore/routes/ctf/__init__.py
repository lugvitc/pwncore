from __future__ import annotations

from fastapi import APIRouter

from pwncore.models import *
import pwncore.config as config
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
    await Team.create(name="CID Squad" + uuid.uuid4().hex, secret_hash="veryverysecret")
    await Container.create(
        docker_id="letsjustsay1",
        flag="pwncore{this_is_a_test_flag}",
        problem_id=1,
        team_id=1,
    )
    await Hint.create(order=0, problem_id=1, text="This is the first hint")
    await Hint.create(order=1, problem_id=1, text="This is the second hint")
    await Hint.create(order=2, problem_id=1, text="This is the third hint")
    await Hint.create(order=0, problem_id=2, text="This is the third hint")
    await Hint.create(order=1, problem_id=2, text="This is the third hint")


@router.get("/list")
async def ctf_list():
    # Get list of ctfs
    problems = await Problem.all().values()
    return problems


@router.get("/{ctf_id}")
async def ctf_get(ctf_id: int):
    problem = await Problem.get_or_none(id=ctf_id)
    return problem


# @router.get("/flag/{ctf_id}")
@router.get("/flag/{ctf_id}/{flag}")
async def flag_get(ctf_id: int, flag: str):
    # flag = await Container.filter(problem_id=ctf_id, team_id=get_team_id(), flag=flag).values()
    flag = await Container.check_flag(
        flag=flag, team_id=get_team_id(), problem_id=ctf_id
    )
    return flag


@router.get("/hint/{ctf_id}")
async def hint_get(ctf_id: int):
    hint = await Hint.return_hint(ctf_id, get_team_id())
    return hint


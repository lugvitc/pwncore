import asyncio
from datetime import date
import itertools
import logging
import uuid

from fastapi import APIRouter, Request, Response
from passlib.hash import bcrypt
from tortoise.transactions import atomic, in_transaction
from tortoise.expressions import RawSQL, Q
from tortoise.functions import Sum

from pwncore.models import (
    Team,
    Problem,
    Hint,
    User,
    PreEventSolvedProblem,
    PreEventProblem,
)
from pwncore.config import config
from pwncore.models.container import Container
from pwncore.models.ctf import SolvedProblem
from pwncore.models.pre_event import PreEventUser
from pwncore.container import docker_client
from pwncore.models.round2 import R2Container, R2Ports, R2Problem
from pwncore.models.user import MetaTeam

metadata = {
    "name": "admin",
    "description": "Admin routes (currently only running when development on)",
}

# TODO: Make this protected
router = APIRouter(prefix="/admin", tags=["admin"])

if config.development:
    logging.basicConfig(level=logging.INFO)

ADMIN_HASH = "$2b$12$K2LsLGS/Mahksh0V6xZYKOviNEHMv3Of5f1zhyF6CWJ8rJIcKnSqu"
NAMES = [
    "Mimas",
    "Enceladus",
    "Tethys",
    "Dione",
    "Rhea",
    "Titan",
    "Hyperion",
    "Iapetus",
    "Phoebe",
    "Janus",
    "Epimetheus",
    "Pan",
]


async def _del_cont(id: str):
    container = await docker_client.containers.get(id)
    await container.kill()
    await container.delete()


@atomic()
async def _create_container(prob: R2Problem, mteam: MetaTeam):
    try:
        container = await docker_client.containers.run(
            name=f"{mteam.name}_{prob.pk}_{uuid.uuid4().hex}",
            config={
                "Image": prob.image_name,
                # Detach stuff
                "AttachStdin": False,
                "AttachStdout": False,
                "AttachStderr": False,
                "Tty": False,
                "OpenStdin": False,
                **prob.image_config,
            },
        )

        container_flag = f"{config.flag}{{{uuid.uuid4().hex}}}"

        await (
            await container.exec(["/bin/bash", "/root/gen_flag", container_flag])
        ).start(detach=True)

        db_container = await R2Container.create(
            docker_id=container.id, problem=prob, meta_tam=mteam, flag=container_flag
        )

        ports = []
        for guest_port in prob.image_config["PortBindings"]:
            port = int((await container.port(guest_port))[0]["HostPort"])
            ports.append(R2Ports(port=port, container=db_container))

        await R2Ports.bulk_create(ports)
    except Exception as err:
        try:
            await container.kill()
            await container.delete()
        except Exception:
            pass
        logging.exception("Error while starting", exc_info=err)


@router.get("/round2")
async def round2(response: Response, req: Request):
    if not bcrypt.verify((await req.body()).strip(), ADMIN_HASH):
        response.status_code = 401
        return

    containers = await Container.all()

    async with in_transaction():
        async with asyncio.TaskGroup() as tg:
            for container in containers:
                tg.create_task(_del_cont(container.docker_id))

        try:
            await Container.all().delete()
        except Exception:
            response.status_code = 500
            logging.exception("Error while initing round2")
            return {"msg_code": config.msg_codes["db_error"]}

        await MetaTeam.all().delete()
        await MetaTeam.bulk_create(
            [MetaTeam(name=NAMES[i], id=i + 1) for i in range(12)]
        )

        teams = (
            await Team.all()
            .filter(Q(solved_problem__problem__visible=True) | Q(points__gte=0))
            .annotate(
                tpoints=RawSQL(
                    'COALESCE((SUM("solvedproblem"."penalty" * '
                    '"solvedproblem__problem"."points")'
                    ' + "team"."points"), 0)'
                )
            )
            .annotate(
                tpoints2=Sum(
                    RawSQL(
                        '"solvedproblem"."penalty" * "solvedproblem__problem"."points"'
                    )
                )
            )
            .order_by("-tpoints")
        )

        for i in range(12):
            for team in teams[i::12]:
                team.meta_team_id = i + 1  # type: ignore[attr-defined]
                # print(mts[i].pk, mts)
                await team.save(update_fields=["meta_team_id"])

        # await Team.bulk_update(teams, fields=["meta_team_id"])

        problems = await R2Problem.all()
        mteams = await MetaTeam.all()

        async with asyncio.TaskGroup() as tg:
            for pm in itertools.product(problems, mteams):
                tg.create_task(_create_container(*pm))


@router.get("/union")
async def calculate_team_coins(
    response: Response, req: Request
):  # Inefficient, anyways will be used only once
    if not bcrypt.verify((await req.body()).strip(), ADMIN_HASH):
        response.status_code = 401
        return
    async with in_transaction():
        logging.info("Calculating team points form pre-event CTFs:")
        team_ids = await Team.filter().values_list("id", flat=True)
        for team_id in team_ids:
            member_tags = await User.filter(team_id=team_id).values_list(
                "tag", flat=True
            )

            if not member_tags:
                return 0

            problems_solved = set(
                await PreEventSolvedProblem.filter(user_id__in=member_tags).values_list(
                    "problem_id", flat=True
                )
            )

            team = await Team.get(id=team_id)
            for ctf_id in problems_solved:
                team.coins += (await PreEventProblem.get(id=ctf_id)).points
            logging.info(f"{team.id}) {team.name}: {team.coins}")
            await team.save()


@router.get("/create")
async def init_db(
    response: Response, req: Request
):  # Inefficient, anyways will be used only once
    if not bcrypt.verify((await req.body()).strip(), ADMIN_HASH):
        response.status_code = 401
        return
    await Problem.create(
        name="Invisible-Incursion",
        description="Chod de tujhe se na ho paye",
        author="Meetesh Saini",
        points=300,
        image_name="key:latest",
        image_config={"PortBindings": {"22/tcp": [{}]}},
        mi=200,
        ma=400,
    )
    await PreEventProblem.create(
        name="Static_test",
        description="Chod de tujhe se na ho paye",
        author="Meetesh Saini",
        points=20,
        flag="asd",
        url="lugvitc.org",
        date=date.today(),
    )
    await PreEventProblem.create(
        name="New Static Test",
        description="AJJSBFISHDBFHSD",
        author="Meetesh Saini",
        points=21,
        flag="asdf",
        url="lugvitc.org",
        date=date.today(),
    )
    await PreEventProblem.create(
        name="Static_test2",
        description="Chod de tujhe se na ho payga",
        author="Meetesh_Saini",
        points=23,
        flag="asd",
        url="http://lugvitc.org",
        date=date.today(),
    )
    await Problem.create(
        name="In-Plain-Sight",
        description="A curious image with hidden secrets?",
        author="KreativeThinker",
        points=300,
        image_name="key:latest",
        image_config={"PortBindings": {"22/tcp": [{}]}},
        mi=200,
        ma=400,
    )
    await Problem.create(
        name="GitGood",
        description="How to master the art of solving CTFs? Git good nub.",
        author="Aadivishnu and Shoubhit",
        points=300,
        image_name="test:latest",
        image_config={"PortBindings": {"22/tcp": [{}], "5000/tcp": [{}]}},
    )
    await Team.create(name="CID Squad", secret_hash=bcrypt.hash("veryverysecret"))
    await Team.create(
        name="Triple A battery", secret_hash=bcrypt.hash("chotiwali"), coins=20
    )
    await PreEventUser.create(tag="23BCE1000", email="dd@ff.in")
    await PreEventUser.create(tag="23BRS1000", email="d2d@ff.in")
    await PreEventSolvedProblem.create(user_id="23BCE1000", problem_id="1")
    await PreEventSolvedProblem.create(user_id="23BRS1000", problem_id="1")
    # await PreEventSolvedProblem.create(
    #     tag="23BAI1000",
    #     problem_id="2"
    # )
    await User.create(
        tag="23BRS1000",
        name="abc",
        team_id=2,
        phone_num=1111111111,
        email="email1@xyz.org",
    )
    await User.create(
        tag="23BCE1000",
        name="def",
        team_id=2,
        phone_num=2222222222,
        email="email1@xyz.org",
    )
    await User.create(
        tag="23BAI1000",
        name="ghi",
        team_id=2,
        phone_num=3333333333,
        email="email1@xyz.org",
    )
    await User.create(
        tag="23BRS2000",
        name="ABC",
        team_id=1,
        phone_num=4444444444,
        email="email1@xyz.org",
    )
    await User.create(
        tag="23BCE2000",
        name="DEF",
        team_id=1,
        phone_num=5555555555,
        email="email1@xyz.org",
    )
    await User.create(
        tag="23BAI2000",
        name="GHI",
        team_id=1,
        phone_num=6666666666,
        email="email1@xyz.org",
    )
    await Hint.create(order=0, problem_id=1, text="This is the first hint")
    await Hint.create(order=1, problem_id=1, text="This is the second hint")
    await Hint.create(order=2, problem_id=1, text="This is the third hint")
    await Hint.create(order=0, problem_id=2, text="This is the first hint")
    await Hint.create(order=1, problem_id=2, text="This is the second hint")
    await SolvedProblem.create(team_id=2, problem_id=1)
    await SolvedProblem.create(team_id=2, problem_id=2)
    await SolvedProblem.create(team_id=1, problem_id=2)

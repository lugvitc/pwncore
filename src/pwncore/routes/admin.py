import logging
import os
import shutil
from datetime import date

import psutil
from fastapi import APIRouter, HTTPException, Request, Response, status, Depends
from fastapi.responses import JSONResponse
from passlib.hash import bcrypt, bcrypt_sha256
from tortoise.transactions import atomic, in_transaction

import pwncore.containerASD as containerASD
from pwncore.config import config
from pwncore.models import (
    Container,
    Hint,
    PreEventProblem,
    PreEventSolvedProblem,
    Problem,
    Team,
    User,
)
from pwncore.models.ctf import SolvedProblem
from pwncore.models.pre_event import PreEventUser

metadata = {
    "name": "admin",
    "description": "Admin routes (currently only running when development on)",
}


async def validate_password(req: Request) -> None:
    """Validate admin password hash."""
    try:
        if not bcrypt_sha256.verify((req.cookies["password"]).strip(), config.admin_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    except KeyError as err:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED) from err


# TODO: Make this protected
router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(validate_password)],
)

if config.development:
    logging.basicConfig(level=logging.INFO)

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
    container = await containerASD.docker_client.containers.get(id)
    await container.kill()
    await container.delete()


@atomic()
@router.get("/union")
async def calculate_team_coins(
    response: Response, req: Request
):  # Inefficient, anyways will be used only once
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
    await Problem.create(
        name="Invisible-Incursion",
        description="Chod de tujhe se na ho paye",
        author="Meetesh Saini",
        points=300,
        image_name="key:latest",
        # image_config={"PortBindings": {"22/tcp": [{}]}},
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
        description="Chod de tujhe se na payga",
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
        # image_config={"PortBindings": {"22/tcp": [{}]}},
        mi=200,
        ma=400,
    )
    await Problem.create(
        name="GitGood",
        description="How to master the art of solving CTFs? Git good nub.",
        author="Aadivishnu and Shoubhit",
        points=300,
        image_name="reg.lugvitc.net/key:latest",
        # image_config={"PortBindings": {"22/tcp": [{}]}},
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


@router.get("/resources")
async def get_resource_usage(response: Response, req: Request):
    cpu_percent = psutil.cpu_percent(interval=1, percpu=False)
    cpu_per_core = psutil.cpu_percent(interval=1, percpu=True)

    memory = psutil.virtual_memory()
    disk = psutil.disk_usage("/")

    db_containers = await Container.all().prefetch_related("team", "problem", "ports")

    containers_info = []
    total_container_memory = 0
    total_container_cpu = 0.0

    for db_container in db_containers:
        ports = [port.port for port in await db_container.ports.all()]

        try:
            container = await containerASD.docker_client.containers.get(
                db_container.docker_id
            )
            stats = await container.stats(stream=False)

            # Handle case where stats might be a list (take first element)
            if isinstance(stats, list):
                stats = stats[0] if stats else {}

            cpu_delta = (
                stats["cpu_stats"]["cpu_usage"]["total_usage"]
                - stats["precpu_stats"]["cpu_usage"]["total_usage"]  # noqa: W503
            )
            system_delta = (
                stats["cpu_stats"]["system_cpu_usage"]
                - stats["precpu_stats"]["system_cpu_usage"]  # noqa: W503
            )
            cpu_usage = 0.0
            if system_delta > 0 and cpu_delta > 0:
                cpu_count = stats["cpu_stats"].get("online_cpus", len(cpu_per_core))
                cpu_usage = (cpu_delta / system_delta) * cpu_count * 100.0

            memory_usage = stats["memory_stats"].get("usage", 0)
            memory_limit = stats["memory_stats"].get("limit", 0)
            memory_percent = 0.0
            if memory_limit > 0:
                memory_percent = (memory_usage / memory_limit) * 100.0

            networks = stats.get("networks", {})
            network_rx = sum(net.get("rx_bytes", 0) for net in networks.values())
            network_tx = sum(net.get("tx_bytes", 0) for net in networks.values())

            total_container_memory += memory_usage
            total_container_cpu += cpu_usage

            container_info = {
                "container_id": db_container.docker_id[:12],
                "team_id": db_container.team_id,
                "team_name": (
                    (await db_container.team).name if db_container.team else "Unknown"
                ),
                "problem_id": db_container.problem_id,
                "problem_name": (
                    (await db_container.problem).name
                    if db_container.problem
                    else "Unknown"
                ),
                "ports": ports,
                "cpu_percent": round(cpu_usage, 2),
                "memory": {
                    "usage": memory_usage,
                    "limit": memory_limit,
                    "percent": round(memory_percent, 2),
                    "usage_mb": round(memory_usage / (1024**2), 2),
                    "limit_mb": round(memory_limit / (1024**2), 2),
                },
                "network": {
                    "rx_bytes": network_rx,
                    "tx_bytes": network_tx,
                    "rx_mb": round(network_rx / (1024**2), 2),
                    "tx_mb": round(network_tx / (1024**2), 2),
                },
            }

            containers_info.append(container_info)

        except Exception as e:
            logging.error(
                f"Error getting stats for container\
                      {db_container.docker_id[:12]}: {str(e)}"
            )
            containers_info.append(
                {
                    "container_id": db_container.docker_id[:12],
                    "team_id": db_container.team_id,
                    "team_name": (
                        (await db_container.team).name
                        if db_container.team
                        else "Unknown"
                    ),
                    "problem_id": db_container.problem_id,
                    "problem_name": (
                        (await db_container.problem).name
                        if db_container.problem
                        else "Unknown"
                    ),
                    "ports": ports,
                    "status": "error",
                    "error": str(e),
                }
            )

    return {
        "system": {
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "disk_percent": disk.percent,
        },
        "containers": {
            "count": len(containers_info),
            "details": containers_info,
        },
    }


@router.get("/docker/list")
async def list_docker_containers(response: Response, req: Request):
    containers = await Container.all().prefetch_related("team", "problem", "ports")
    container_list = []

    for container in containers:
        ports = [port.port for port in await container.ports.all()]
        container_info = {
            "docker_id": container.docker_id,
            "team_id": container.team_id,
            "team_name": container.team.name if container.team else "Unknown",
            "problem_id": container.problem_id,
            "problem_name": container.problem.name if container.problem else "Unknown",
            "ports": ports,
        }
        container_list.append(container_info)

    return {"containers": container_list}


@router.get("/docker/{docker_id}/log")
async def get_docker_container_log(docker_id: str, response: Response, req: Request):
    try:
        container = await containerASD.docker_client.containers.get(docker_id)
        logs = await container.log(stdout=True, stderr=True, follow=False)
        return {"logs": logs}
    except Exception as e:
        response.status_code = 404
        return {"error": f"Container not found or error retrieving logs: {str(e)}"}


@router.post("/stopall")
async def stopall_containers(response: Response, req: Request):
    async with in_transaction():
        containers = await Container.all().values()

        try:
            await Container.all().delete()
        except Exception:
            response.status_code = 500
            return {"msg_code": config.msg_codes["db_error"]}

        if os.path.exists(config.staticfs_data_dir):
            shutil.rmtree(config.staticfs_data_dir)
            os.makedirs(config.staticfs_data_dir)

        for db_container in containers:
            try:
                await _del_cont(db_container["docker_id"])
            except Exception:
                pass

        return {"msg_code": config.msg_codes["containers_team_stop"]}


@router.post("/stop/{ctf_id}")
async def stop_containers_for_ctf(ctf_id: int, response: Response, req: Request):
    async with in_transaction():
        ctf = await Problem.get_or_none(id=ctf_id)
        if not ctf:
            response.status_code = 404
            return {"msg_code": config.msg_codes["ctf_not_found"]}

        containers = await Container.filter(problem_id=ctf_id).values()

        try:
            await Container.filter(problem_id=ctf_id).delete()
        except Exception:
            response.status_code = 500
            return {"msg_code": config.msg_codes["db_error"]}

        for db_container in containers:
            if ctf.static_files:
                static_path = f"{config.staticfs_data_dir}/\
                    {db_container['team_id']}/{db_container['docker_id']}"
                if os.path.exists(static_path):
                    shutil.rmtree(static_path)
            else:
                try:
                    await _del_cont(db_container["docker_id"])
                except Exception:
                    pass

        return {"msg_code": config.msg_codes["container_stop"]}


@router.post("/docker/stop/{docker_id}")
async def stop_docker_container(docker_id: str, response: Response, req: Request):
    container = await Container.get_or_none(docker_id=docker_id)
    if not container:
        response.status_code = 404
        return {"error": "Container not found"}

    try:
        await Container.filter(docker_id=docker_id).delete()
        ctf = await container.problem
        if ctf and ctf.static_files:
            static_path = f"{config.staticfs_data_dir}/{container.team_id}/{docker_id}"
            if os.path.exists(static_path):
                shutil.rmtree(static_path)
        else:
            try:
                await _del_cont(docker_id)
            except Exception:
                pass
    except Exception:
        response.status_code = 500
        return {"msg_code": config.msg_codes["db_error"]}

    return {"msg_code": config.msg_codes["container_stop"]}


@router.get("/ban/list")
async def get_ban_list(request: Request, response: Response) -> JSONResponse:
    """Get banned tags list."""
    return {"banned": config.blacklist}


@router.post("/ban/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
async def ban_tag(request: Request, response: Response, team_id: int) -> None:
    """Add the provided tag to the blacklist."""
    if team_id not in config.blacklist:
        config.blacklist.append(team_id)


@router.post("/unban/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
async def unban_tag(request: Request, response: Response, team_id: int) -> None:
    """Remove the provided tag from the blacklist."""
    try:
        config.blacklist.remove(team_id)
    except ValueError:
        return

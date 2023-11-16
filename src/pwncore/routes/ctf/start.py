from __future__ import annotations

from fastapi import APIRouter, Response
import uuid
from tortoise.transactions import atomic
import logging

from pwncore.db import Container, CTF
from pwncore.container import docker_client
from pwncore.config import config

# temporary helper functions
def get_team_id():
    return 34
def get_empty_ports():
    return [4444]


router = APIRouter(tags=["ctf"])


@atomic()
@router.post("/start/{ctf_id}")
async def start_docker_container(ctf_id: int, response: Response):

    # Testing purposes
    """
    image_config format:

    """
    await CTF.create(**{
        "name": "Invisible-Incursion",
        "docker_config": {
            "Image": "key:latest",
            "AttachStdin": False,
            "AttachStdout": False,
            "AttachStderr": False,
            "Tty": False,
            "OpenStdin": False,
            "PortBindings": {
                "22/tcp": []
            }
        }
    })

    ctf = await CTF.get_or_none(id=ctf_id)
    if not ctf:
        response.status_code = 404
        return {"msg_code": config.msg_codes["ctf_not_found"]}

    team_id = get_team_id()  # From JWT
    team_container = await Container.get_or_none(team_id=team_id, ctf_id=ctf_id)
    if team_container:
        return {
            "msg_code": config.msg_codes["container_already_running"],
            "ports": team_container.ports.split(","),
            "ctf_id": team_container.ctf_id
        }

    if await Container.filter(team_id=team_id).count() >= config.max_containers_per_team:
        return {
            "msg_code": config.msg_codes["container_limit_reached"]
        }

    # Start a new container
    container_name = f"{team_id}_{ctf_id}_{uuid.uuid4().hex}"
    container_flag = f"{config.flag}{{{uuid.uuid4().hex}}}"
    image_config = ctf.docker_config

    # Ports
    port_list = get_empty_ports()  # Need to implement

    if len(port_list) < len(image_config["PortBindings"]):
        # Handle error here
        logging.critical("No more free ports available on machine.")
        response.status_code = 500
        return {"msg_code": config.msg_codes["port_limit_reached"]}

    ports = []  # Only to save the host ports used to return to the user
    for guest_port in image_config["PortBindings"]:
        port = port_list.pop()
        ports.append(port)
        image_config["PortBindings"][guest_port] = [{"HostPost": port}]

    # Run
    container = await docker_client.containers.run({
        "Image": "key:latest",
        "AttachStdin": False,
        "AttachStdout": False,
        "AttachStderr": False,
        "Tty": False,
        "OpenStdin": False,
        "PortBindings": {
            "22/tcp": [{"HostPort": "4444"}]
        }
    }, name=container_name)

    await (
        await container.exec(["/bin/bash", "/root/gen_flag", container_flag])
    ).start(detach=True)

    try:
        await Container.create(**{
            "id"        : container.id,
            "name"      : container_name,
            "team_id"   : team_id,
            "ctf_id"    : ctf_id,
            "flag"      : container_flag,
            "ports"     : ','.join([str(port) for port in ports])       # Save ports as csv
        })
    except Exception as e:
        # Stop the container if failed to make a DB record
        await container.stop()
        await container.delete()

        logging.critical(e)
        response.status_code = 500
        return {
            "msg_code": config.msg_codes["db_error"]
        }

    return {
        "msg_code": config.msg_codes["container_start"],
        "ports": ports,
        "ctf_id": ctf_id
    }


@atomic()
@router.post("/stopall")
async def stopall_docker_container(response: Response):

    team_id = get_team_id()  # From JWT

    containers = await Container.filter(team_id=team_id).values()

    # We first try to delete the record from the DB
    # Then we stop the container
    try:
        await Container.filter(team_id=team_id).delete()
    except Exception:
        response.status_code = 500
        return {
            "msg_code": config.msg_codes["db_error"]
        }

    for db_container in containers:
        container = await docker_client.containers.get(db_container.id)
        await container.stop()
        await container.delete()

    return {"msg_code": config.msg_codes["containers_team_stop"]}


@atomic()
@router.post("/stop/{ctf_id}")
async def stop_docker_container(ctf_id: int, response: Response):

    ctf = await CTF.get_or_none(id=ctf_id)
    if not ctf:
        response.status_code = 404
        return {"msg_code": config.msg_codes["ctf_not_found"]}

    team_id = get_team_id()
    team_container = await Container.get_or_none(team_id=team_id, ctf_id=ctf_id)
    if not team_container:
        return {"msg_code": config.msg_codes["container_not_found"]}

    # We first try to delete the record from the DB
    # Then we stop the container
    try:
        await Container.filter(team_id=team_id, ctf_id=ctf_id).delete()
    except Exception:
        response.status_code = 500
        return {
            "msg_code": config.msg_codes["db_error"]
        }

    container = await docker_client.containers.get(team_container.id)
    await container.stop()
    await container.delete()

    return {"msg_code": config.msg_codes["container_stop"]}

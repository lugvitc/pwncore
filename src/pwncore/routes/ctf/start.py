from __future__ import annotations

from fastapi import Response
import uuid
from tortoise.transactions import atomic

from pwncore.routes.ctf import router
from pwncore.db import Container, CTF
from pwncore.container import docker_client
from pwncore.config import DEV_CONFIG

config = DEV_CONFIG

# UNTESTED


@atomic()
@router.post("/start/{ctf_id}")
async def start_docker_container(ctf_id: int, response: Response):

    ctf = await CTF.get_or_none(id=ctf_id)
    if not ctf:
        response.status_code = 404
        return {"msg": config.messages["ctf_not_found"]}

    team_id = get_team_id()  # From JWT
    team_container = Container.get_or_none(team_id=team_id, ctf_id=ctf_id)
    if not team_container:
        return {
            "msg": config.messages["container_already_running"],
            "ports": team_container.ports.split(","),
            "ctf_id": team_container.ctf_id
        }

    if Container.filter(team_id=team_id).count() >= config.max_containers_per_team:
        return {
            "msg": config.messages["container_limit_reached"]
        }

    # Start a new container
    image_config = ctf.image_config.copy()
    """
    This image_config will look like:
    {
        "ports": {
            "22/tcp": None,
            "80/tcp": None
        }
    }

    `None` gets substitued with the empty ports on the host system.
    """

    # Ports
    port_list = get_empty_ports() # Need to implement

    if len(port_list) < len(image_config["ports"]):
        # Handle error here
        print("AAAAAAAAAAAAAAAAAAA")
        response.status_code = 500
        return {"msg": config.messages["port_limit_reached"]}

    ports = []  # Only to save the host ports used to return to the user
    for guest_port in image_config["ports"]:
        port = port_list.pop()
        ports.append(port)
        image_config["ports"][guest_port] = port

    # Run
    container = docker_client.containers.run(
        ctf.image_name,
        detach=True,
        name=f"{team_id}_{ctf_id}",
        **image_config
    )

    flag = f"{DEV_CONFIG.flag}{{{uuid.uuid4().hex}}}"
    container.exec_run(
        f"/bin/bash /root/gen_flag '{flag}'",
        user="root"
    )

    try:
        await Container.create(**{
            "id"        : container.id,
            "name"      : container.name,
            "team_id"   : team_id,
            "ctf_id"    : ctf_id,
            "flag"      : flag,
            "ports"     : ','.join(ports)       # Save ports as csv
        })
    except:  # Not sure which exception should be filtered here for
        # Stop the container
        container.stop()
        container.remove()

        response.status_code = 500
        return {
            "msg": config.messages["db_error"]
        }

    return {
        "msg": config.messages["container_started"],
        "ports": ports,
        "ctf_id": ctf_id
    }


@atomic()
@router.post("/stopall")
async def stop_docker_container(response: Response):

    team_id = get_team_id() # From JWT

    containers = Container.filter(team_id=team_id).values()

    # We first try to delete the record from the DB
    # Then we stop the container
    try:
        await Container.filter(team_id=team_id).delete()
        await Container.save()
    except:
        response.status_code = 500
        return {
            "msg": config.messages["db_error"]
        }

    for db_container in containers:
        container = docker_client.containers.get(db_container.id)
        container.stop()
        container.remove()

    return {"msg": config.messages["containers_team_stop"]}


@atomic()
@router.post("/stop/{ctf_id}")
async def stop_docker_container(ctf_id: int, response: Response):

    ctf = await CTF.get_or_none(id=ctf_id)
    if not ctf:
        response.status_code = 404
        return {"msg": config.messages["ctf_not_found"]}

    team_id = get_team_id()
    team_container = Container.get_or_none(team_id=team_id, ctf_id=ctf_id)
    if not team_container:
        return {"msg": config.messages["container_not_found"]}

    # We first try to delete the record from the DB
    # Then we stop the container
    try:
        await Container.filter(team_id=team_id, ctf_id=ctf_id).delete()
        await Container.save()
    except:  # Not sure which exception should be filtered here for
        response.status_code = 500
        return {
            "msg": config.messages["db_error"]
        }

    container = docker_client.containers.get(team_container.id)
    container.stop()
    container.remove()

    return {"msg": config.messages["container_stop"]}

from __future__ import annotations

from fastapi import Response
import uuid
from tortoise.transactions import atomic

from pwncore.routes.ctf import router
from pwncore.db import Container, CTF
from pwncore.container import docker_client
from pwncore.config import DEV_CONFIG

# UNTESTED


@atomic()
@router.post("/start/{ctf_id}")
async def start_docker_container(ctf_id: int, response: Response):

    if not await CTF.filter(id=ctf_id).exists():
        response.status_code = 404
        return {"msg": "CTF does not exist."}
    ctf = await CTF.get(id=ctf_id)

    user_id = get_user_id()  # From JWT
    if await Container.filter(user_id=user_id).exists():
        user_container = Container.get(user_id=user_id)
        return {
            "msg": "You already have a running container for a CTF.",
            "ports": user_container.ports.split(","),
            "ctf_id": user_container.ctf_id
        }

    team_id = get_team_id()  # From JWT
    if await Container.filter(team_id=team_id, ctf_id=ctf_id).exists():
        team_container = Container.get(team_id=team_id, ctf_id=ctf_id)
        return {
            "msg": "Your team already has a running container for this CTF.",
            "ports": team_container.ports.split(","),
            "ctf_id": team_container.ctf_id
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
        return {"msg": "Server ran out of ports 💀"}

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

    await Container.create(**{
        "id"        : container.id,
        "name"      : container.name,
        "user_id"   : user_id
        "team_id"   : team_id,
        "ctf_id"    : ctf_id,
        "flag"      : flag,
        "ports"     : ','.join(ports)       # Save ports as csv
    })
    await Container.save()

    return {
        "msg": "Container started.",
        "ports": ports,
        "ctf_id": ctf_id
    }

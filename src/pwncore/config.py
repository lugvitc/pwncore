from dataclasses import dataclass

"""
Sample messages:
"db_error": "An error occurred, please try again.",
"port_limit_reached": "Server ran out of ports 💀",
"ctf_not_found": "CTF does not exist.",
"container_start": "Container started.",
"container_stop": "Container stopped.",
"containers_team_stop": "All team containers stopped.",
"container_not_found": "You have no running containers for this CTF.",
"container_already_running": "Your team already has a running container for this CTF.",
"container_limit_reached": "Your team already has reached the maximum number of containers limit, please stop other unused containers."
"""

msg_codes = {
    "db_error": 0,
    "port_limit_reached": 1,
    "ctf_not_found": 2,
    "container_start": 3,
    "container_stop": 4,
    "containers_team_stop": 5,
    "container_not_found": 6,
    "container_already_running": 7,
    "container_limit_reached": 8
}


@dataclass
class Config:
    development: bool
    msg_codes: dict
    db_url: str
    flag: str
    max_containers_per_team: int


config = Config(
    development=True,
    db_url="sqlite://:memory:",
    flag="C0D",
    max_containers_per_team=3,
    msg_codes={
        "db_error": 0,
        "port_limit_reached": 1,
        "ctf_not_found": 2,
        "container_start": 3,
        "container_stop": 4,
        "containers_team_stop": 5,
        "container_not_found": 6,
        "container_already_running": 7,
        "container_limit_reached": 8
    }
)

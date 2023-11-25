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
"container_limit_reached": "Your team already has reached the maximum number"
                           " of containers limit, please stop other unused containers."
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
    "container_limit_reached": 8,
    "hint_limit_reached": 9,
    "team_not_found": 10,
    "user_not_found": 11,
    "ctf_solved": 12,
    "signup_success": 13,
    "wrong_password": 14,
    "login_success": 15,
    "team_not_found": 16,
    "team_exists": 17,
}


@dataclass
class Config:
    development: bool
    msg_codes: dict
    db_url: str
    docker_url: str | None
    flag: str
    max_containers_per_team: int
    jwt_secret: str
    jwt_valid_duration: int


config = Config(
    development=True,
    db_url="sqlite://:memory:",
    docker_url=None,  # None for default system docker
    flag="C0D",
    max_containers_per_team=3,
    jwt_secret="mysecret",
    jwt_valid_duration=12,  # In hours
    msg_codes=msg_codes,
)

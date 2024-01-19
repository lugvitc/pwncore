from dataclasses import dataclass
from os import getenv
from sys import stderr

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
    "team_exists": 17,
    "user_added": 18,
    "user_removed": 19,
    "user_already_in_team": 20,
    "user_not_in_team": 21,
    "insufficient_coins": 22,
    "user_or_email_exists": 23,
    "users_not_found": 24,
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
    hint_penalty: int
    max_members_per_team: int


db_url = getenv("DATABASE_URL")
docker_url = getenv("DOCKER_URL")
secret = getenv("JWT_SECRET")

# do export PYTHONOPTIMIZE=2 in prod please

if db_url is None:
    print("DATABASE_URL environment variable not set", file=stderr)
    raise SystemExit(1)

if secret is None and __debug__ is False:
    print("JWT_SECRET environment variables not set", file=stderr)
    raise SystemExit(1)
else:
    secret = "12345678"

config = Config(
    development=True,
    db_url=db_url,
    # docker_url=None,  # None for default system docker
    # Or set it to an arbitrary URL for testing without Docker
    docker_url=docker_url,
    flag="PWNCOR3",
    max_containers_per_team=3,
    jwt_secret=secret,
    jwt_valid_duration=12,  # In hours
    msg_codes=msg_codes,
    hint_penalty=10,
    max_members_per_team=3,
)

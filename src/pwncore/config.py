from __future__ import annotations

import typing as t

__all__ = (
    "Config",
    "BaseConfig",
)


class Config(t.Protocol):
    development:                bool
    flag:                       str
    max_containers_per_team:    int
    messages:                   dict


class BaseConfig(Config):
    __slots__ = ("development",)

    flag = "C0D"
    max_containers_per_team = 3
    messages = {
        "db_error": "An error occured, please try again.",

        "port_limit_reached": "Server ran out of ports 💀",

        "ctf_not_found": "CTF does not exist.",

        "container_start": "Container started.",
        "container_stop": "Container stopped.",
        "containers_team_stop": "All team containers stopped.",
        "container_not_found": "You have no running containers for this CTF.",
        "container_already_running": "Your team already has a running container for this CTF.",
        "container_limit_reached": "Your team already has reached the maximum number of containers limit, please stop other unused containers."
    }

    def __init__(self, development: bool) -> None:
        self.development = development

DEV_CONFIG: t.Final[BaseConfig] = BaseConfig(True)

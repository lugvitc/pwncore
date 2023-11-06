from __future__ import annotations

import typing as t

__all__ = (
    "Config",
    "BaseConfig",
)


class Config(t.Protocol):
    development: bool


class BaseConfig(Config):
    __slots__ = ("development",)

    def __init__(self, development: bool) -> None:
        self.development = development


DEV_CONFIG: t.Final[BaseConfig] = BaseConfig(True)

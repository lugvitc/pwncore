"""pwncore.models

Contains all Pydantic and Tortoise ORM models
"""

import typing

import tortoise
from tortoise.contrib.pydantic.creator import pydantic_model_creator

from pwncore.models.container import Container, Ports
from pwncore.models.ctf import (
    BaseProblem,
    BaseProblem_Pydantic,
    Hint,
    Hint_Pydantic,
    Problem,
    Problem_Pydantic,
    SolvedProblem,
    ViewedHint,
)
from pwncore.models.powerups import Powerup, Powerup_Pydantic, PowerupType
from pwncore.models.pre_event import (
    PreEventProblem,
    PreEventProblem_Pydantic,
    PreEventSolvedProblem,
    PreEventUser,
)
from pwncore.models.round2 import R2AttackRecord, R2Container, R2Ports, R2Problem
from pwncore.models.user import (
    MetaTeam,
    MetaTeam_Pydantic,
    Team,
    Team_Pydantic,
    User,
    User_Pydantic,
)

__all__ = (
    "Problem",
    "BaseProblem_Pydantic",
    "Hint",
    "Hint_Pydantic",
    "SolvedProblem",
    "ViewedHint",
    "Container",
    "Ports",
    "User",
    "PreEventSolvedProblem",
    "PreEventProblem",
    "PreEventUser",
    "User_Pydantic",
    "Team",
    "Team_Pydantic",
    "MetaTeam",
    "MetaTeam_Pydantic",
    "PreEventProblem_Pydantic",
    "Problem_Pydantic",
    "BaseProblem",
    "R2Problem",
    "R2Ports",
    "R2Container",
    "R2Container_Pydantic",
    "R2AttackRecord",
    "Powerup",
    "PowerupType",
    "Powerup_Pydantic",
)


def get_annotations(cls, method=None):
    return typing.get_type_hints(method or cls)


tortoise.contrib.pydantic.utils.get_annotations = get_annotations  # type: ignore[unused-ignore]
tortoise.contrib.pydantic.creator.get_annotations = get_annotations  # type: ignore[unused-ignore]


tortoise.Tortoise.init_models(["pwncore.models.round2"], "models")
R2Container_Pydantic = pydantic_model_creator(R2Container)

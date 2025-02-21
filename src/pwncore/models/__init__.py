"""pwncore.models

Contains all Pydantic and Tortoise ORM models
"""

import typing

import tortoise

from pwncore.models.container import Container, Ports
from pwncore.models.ctf import (
    Problem,
    SolvedProblem,
    Hint,
    ViewedHint,
    Hint_Pydantic,
    BaseProblem_Pydantic,
    Problem_Pydantic,
    BaseProblem,
)
from pwncore.models.user import (
    User,
    Team,
    Team_Pydantic,
    User_Pydantic,
)
from pwncore.models.pre_event import (
    PreEventProblem,
    PreEventSolvedProblem,
    PreEventUser,
    PreEventProblem_Pydantic,
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
    "PreEventProblem_Pydantic",
    "Problem_Pydantic",
    "BaseProblem",
)


def get_annotations(cls, method=None):
    return typing.get_type_hints(method or cls)


tortoise.contrib.pydantic.utils.get_annotations = get_annotations  # type: ignore[unused-ignore]
tortoise.contrib.pydantic.creator.get_annotations = get_annotations  # type: ignore[unused-ignore]

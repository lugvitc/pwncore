from __future__ import annotations

from tortoise import fields
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.models import Model

from pwncore.models.container import BaseContainer
from pwncore.models.ctf import Problem
from pwncore.models.user import MetaTeam

__all__ = (
    "MetaProblem",
    "MetaProblem_Pydantic",
    "MetaContainer",
    "MetaPorts",
)


class MetaProblem(Problem):
    solved = fields.BooleanField(default=False)


class MetaContainer(BaseContainer):
    meta_problem: fields.ForeignKeyRelation[MetaProblem] = fields.ForeignKeyField(
        "models.MetaProblem", on_delete=fields.OnDelete.NO_ACTION
    )
    meta_team: fields.ForeignKeyRelation[MetaTeam] = fields.ForeignKeyField(
        "models.MetaTeam"
    )
    ports: fields.ReverseRelation[MetaPorts]


class MetaPorts(Model):
    container: fields.ForeignKeyRelation[MetaContainer] = fields.ForeignKeyField(
        "models.MetaContainer", related_name="ports", on_delete=fields.OnDelete.CASCADE
    )
    port = fields.IntField(pk=True)


MetaProblem_Pydantic = pydantic_model_creator(MetaProblem)

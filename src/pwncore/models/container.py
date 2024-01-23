from __future__ import annotations

import typing as t

from tortoise.models import Model
from tortoise import fields

if t.TYPE_CHECKING:
    from pwncore.models.ctf import Problem
    from pwncore.models.user import Team

__all__ = ("BaseContainer", "Container", "Ports")


class BaseContainer(Model):
    docker_id = fields.CharField(128, unique=True)
    flag = fields.TextField()


# Note: These are all type annotated, dont worry
class Container(BaseContainer):
    problem: fields.ForeignKeyRelation[Problem] = fields.ForeignKeyField(
        "models.Problem", on_delete=fields.OnDelete.NO_ACTION
    )
    team: fields.ForeignKeyRelation[Team] = fields.ForeignKeyField("models.Team")

    ports: fields.ReverseRelation[Ports]


class Ports(Model):
    # FUTURE PROOFING: ADD domain
    container: fields.ForeignKeyRelation[Container] = fields.ForeignKeyField(
        "models.Container", related_name="ports", on_delete=fields.OnDelete.CASCADE
    )
    port = fields.IntField(pk=True)

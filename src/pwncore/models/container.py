from __future__ import annotations

import typing as t

from tortoise.models import Model
from tortoise import fields

if t.TYPE_CHECKING:
    from pwncore.models.ctf import Problem


# Note: These are all type annotated, dont worry
class Container(Model):
    id = fields.TextField(pk=True)
    ctf: fields.ForeignKeyRelation[Problem] = fields.ForeignKeyField(
        "models.Problem", on_delete=fields.OnDelete.NO_ACTION
    )
    team_id = fields.IntField()  # TODO: Foreign
    flag = fields.TextField()

    ports: fields.ReverseRelation[Ports]


class Ports(Model):
    # FUTURE PROOFING: ADD domain
    container: fields.ForeignKeyRelation[Container] = fields.ForeignKeyField(
        "models.Container", related_name="ports", on_delete=fields.OnDelete.CASCADE
    )
    port = fields.IntField(pk=True)

from __future__ import annotations

import typing as t

from tortoise.models import Model
from tortoise import fields
from tortoise.fields import ForeignKeyRelation

if t.TYPE_CHECKING:
    from pwncore.models.ctf import CTF


# Note: These are all type annotated, dont worry
class Container(Model):
    id = fields.TextField(pk=True)
    ctf_id: ForeignKeyRelation[CTF] = fields.ForeignKeyField("models.CTF", "id")
    team_id = fields.IntField()  # TODO: Foreign
    flag = fields.TextField()


class Ports(Model):
    # FUTURE PROOFING: ADD domain
    container_id: ForeignKeyRelation[Container] = fields.ForeignKeyField(
        "models.Container", "id"
    )
    port = fields.IntField(pk=True)

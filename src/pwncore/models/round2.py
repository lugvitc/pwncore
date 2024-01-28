from __future__ import annotations

from typing import Any

from tortoise import fields
from tortoise.models import Model

from pwncore.models.ctf import BaseProblem
from pwncore.models.user import MetaTeam

__all__ = ("R2Problem", "R2Container", "R2Ports", "R2AttackRecord")


class R2Problem(BaseProblem):
    image_name = fields.TextField()
    image_config: fields.Field[dict[str, Any]] = fields.JSONField(
        null=True
    )  # type: ignore[assignment]

    class PydanticMeta:
        exclude = [
            "image_name",
            "image_config",
        ]


class R2Container(Model):
    docker_id = fields.CharField(128, unique=True)
    problem: fields.ForeignKeyRelation[R2Problem] = fields.ForeignKeyField(
        "models.R2Problem", on_delete=fields.OnDelete.NO_ACTION
    )
    meta_team: fields.ForeignKeyRelation[MetaTeam] = fields.ForeignKeyField(
        "models.MetaTeam", on_delete=fields.OnDelete.NO_ACTION
    )
    flag = fields.TextField()
    solved = fields.BooleanField(default=False)

    ports: fields.ReverseRelation[R2Ports]

    class PydanticMeta:
        exclude = ["docker_id", "flag", "meta_team", "r2attackrecords"]


class R2Ports(Model):
    container: fields.ForeignKeyRelation[R2Container] = fields.ForeignKeyField(
        "models.R2Container", related_name="ports", on_delete=fields.OnDelete.CASCADE
    )
    port = fields.IntField(pk=True)


class R2AttackRecord(Model):
    container: fields.ForeignKeyRelation[R2Container] = fields.ForeignKeyField(
        "models.R2Container", on_delete=fields.OnDelete.CASCADE
    )

    meta_team: fields.ForeignKeyRelation[MetaTeam] = fields.ForeignKeyField(
        "models.MetaTeam", on_delete=fields.OnDelete.NO_ACTION
    )

from __future__ import annotations

from typing import TYPE_CHECKING

from tortoise import fields
from tortoise.models import Model

if TYPE_CHECKING:
    from pwncore.models.container import Container

# Not too sure here


class User(Model):
    user_name = fields.TextField(unique=True)

    team: fields.ForeignKeyNullableRelation[Team] = fields.ForeignKeyField(
        "models.Team", "id", null=True
    )


class Team(Model):
    team_name = fields.TextField(unique=True)
    secret_hash = fields.TextField()

    # TODO: Add count constraint
    members: fields.ReverseRelation[User]
    containers: fields.ReverseRelation[Container]

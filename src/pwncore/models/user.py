from __future__ import annotations

from tortoise import fields
from tortoise.models import Model

# Not too sure here

class User(Model):
    user_name = fields.TextField(unique=True)

    team: fields.ForeignKeyNullableRelation[Team] = fields.ForeignKeyField("models.Team", "id", null=True)

class Team(Model):
    team_name = fields.TextField(unique=True)
    secret_hash = fields.TextField()

    # TODO: Add count constraint
    members: fields.ReverseRelation[User]

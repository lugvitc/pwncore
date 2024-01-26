from __future__ import annotations

from tortoise import fields
from tortoise.exceptions import IntegrityError
from tortoise.models import Model
from tortoise.expressions import Q
from tortoise.contrib.pydantic import pydantic_model_creator

from pwncore.models.container import Container
from pwncore.config import config

__all__ = (
    "User",
    "Team",
    "MetaTeam",
    "MetaTeam_Pydantic",
    "User_Pydantic",
    "Team_Pydantic",
)


class User(Model):
    # Registration numbers and other identity tags
    # abstractly just represents one person, expand this
    # field for Identity providers
    tag = fields.CharField(128, unique=True)
    name = fields.TextField()
    email = fields.TextField()
    phone_num = fields.CharField(15)

    team: fields.ForeignKeyNullableRelation[Team] = fields.ForeignKeyField(
        "models.Team", "members", null=True, on_delete=fields.OnDelete.SET_NULL
    )

    async def save(self, *args, **kwargs):
        # TODO: Insert/Update in one query
        # Reason why we dont use pre_save: overhead, ugly
        if self.team is not None and hasattr(self.team, "members"):
            count = await self.team.members.filter(~Q(id=self.pk)).count()
            if count >= config.max_members_per_team:
                raise IntegrityError(
                    f"{config.max_members_per_team}"
                    " or more users already exist for the team"
                )
        return await super().save(*args, **kwargs)


class Team(Model):
    id = fields.IntField(
        pk=True
    )  # team.id raises Team does not have id, so explicitly adding it
    name = fields.CharField(255, unique=True)
    secret_hash = fields.TextField()
    coins = fields.IntField(default=0)
    points = fields.IntField(default=0)

    members: fields.ReverseRelation[User]
    containers: fields.ReverseRelation[Container]

    meta_team: fields.ForeignKeyNullableRelation[MetaTeam] = fields.ForeignKeyField(
        "models.MetaTeam", "teams", null=True, on_delete=fields.OnDelete.SET_NULL
    )

    class PydanticMeta:
        exclude = ["secret_hash"]


class MetaTeam(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(255, unique=True)
    points = fields.IntField(default=0)

    teams: fields.ReverseRelation[Team]


Team_Pydantic = pydantic_model_creator(Team)
User_Pydantic = pydantic_model_creator(User)
MetaTeam_Pydantic = pydantic_model_creator(MetaTeam)

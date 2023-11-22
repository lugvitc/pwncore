from __future__ import annotations

from typing import TYPE_CHECKING

from tortoise import fields
from tortoise.exceptions import IntegrityError
from tortoise.models import Model
from tortoise.expressions import Q
from passlib.hash import bcrypt

if TYPE_CHECKING:
    from pwncore.models.container import Container

__all__ = ("User", "Team")


class User(Model):
    # Registration numbers and other identity tags
    # abstractly just represents one person, expand this
    # field for Identity providers
    tag : fields.CharField = fields.CharField(128, unique=True)
    name : str = fields.TextField()
    email : str = fields.TextField()
    phone_num : fields.CharField = fields.CharField(15)

    team: fields.ForeignKeyNullableRelation[Team] = fields.ForeignKeyField(
        "models.Team", "members", null=True, on_delete=fields.OnDelete.SET_NULL
    )

    async def save(self, *args, **kwargs):
        # TODO: Insert/Update in one query
        # Reason why we dont use pre_save: overhead, ugly
        if self.team is not None:
            count = await self.team.members.filter(~Q(id=self.pk)).count()
            if count >= 3:
                raise IntegrityError("3 or more users already exist for the team")
        return await super().save(*args, **kwargs)


class Team(Model):
    name : fields.CharField = fields.CharField(255, unique=True)
    password : fields.CharField = fields.CharField(255, unique=True)
    current_points : int = fields.IntField(null=True)
    current_stage : int = fields.IntField(null=True)
    last_timestamp : fields.DatetimeField = fields.DatetimeField(null=True)

    members: fields.ReverseRelation[User]
    containers: fields.ReverseRelation[Container]

    async def check_password(self, password : str) -> bool:
        return bcrypt.verify(self.password, password)

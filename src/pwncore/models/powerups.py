from enum import Enum

from tortoise import fields
from tortoise.contrib.pydantic.creator import pydantic_model_creator
from tortoise.models import Model

from pwncore.models import Team

__all__ = ("PowerupType", "Powerup", "Powerup_Pydantic")


class PowerupType(str, Enum):
    LUCKY_DRAW = "lucky_draw"
    SABOTAGE = "sabotage"
    GAMBLE = "gamble"
    POINT_SIPHON = "point_siphon"
    FREE_HINT = "free_hint"


class Powerup(Model):
    id = fields.IntField(pk=True)
    type = fields.CharEnumField(PowerupType)
    cost = fields.IntField()
    team: fields.ForeignKeyRelation[Team] = fields.ForeignKeyField(
        "models.Team", related_name="powerups"
    )
    used = fields.BooleanField(default=False)
    created_at = fields.DatetimeField(auto_now_add=True)
    max_count = fields.IntField()


Powerup_Pydantic = pydantic_model_creator(Powerup)

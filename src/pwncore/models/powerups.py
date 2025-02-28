from __future__ import annotations
from datetime import timedelta
from dataclasses import dataclass
from typing import ClassVar
from pydantic import field_serializer

from tortoise import fields
from tortoise.contrib.pydantic.creator import pydantic_model_creator
from tortoise.models import Model

from pwncore.models import (
    AttackDefTeam
)

__all__ = ("PowerupType", "UsedPowerup", "Powerup", "Powerup_Pydantic")

@dataclass
class PowerupType:
    name: str
    cost: int
    max_uses_default: int = 1
    duration: timedelta | None = None
    all_powerup_types: ClassVar[dict[str, PowerupType]] = {}

    def __post_init__(self):
        self.all_powerup_types[self.name] = self

class PowerupTypeField(fields.CharField):
    def __init__(self, **kwargs):
        super().__init__(128, **kwargs)
        # if not issubclass(enum_type, Enum):
            # raise ConfigurationError("{} is not a subclass of Enum!".format(enum_type))
        # self._powerup_type = powerup_type

    def to_db_value(self, powerup_type: PowerupType, instance) -> str:
        return powerup_type.name

    def to_python_value(self, value: PowerupType) -> PowerupType:
        return value

Sabotage = PowerupType(name = "Sabotage", cost = 500, duration = timedelta(seconds=5))
Shield = PowerupType(name = "Shield", cost = 200, max_uses_default = 3, duration = timedelta(seconds=10))
PointSiphon = PowerupType(name = "PointSiphon", cost = 150, duration = timedelta(seconds=15))
Upgrade = PowerupType(name = "Upgrade", cost = 100)

class Powerup(Model):
    id = fields.IntField(pk=True)
    powerup_type = PowerupTypeField()
    attack_def_team: fields.ForeignKeyRelation[AttackDefTeam] = fields.ForeignKeyField(
        "models.AttackDefTeam", related_name="powerups"
    )
    created_at = fields.DatetimeField(auto_now_add=True)
    used_at_least_once = fields.BooleanField(default=False)
    max_uses = fields.IntField(default=1)
    used_count = fields.IntField(default=0)
    used_instance = fields.ReverseRelation["UsedPowerup"]

    async def save(self, *args, **kwargs):
        if not self.max_uses:
            self.max_uses = all_powerup_types[self.powerup_type].max_uses_default
        await super().save(*args, **kwargs)

class UsedPowerup(Model):
    id = fields.IntField(pk=True)
    powerup: fields.ForeignKeyRelation[Powerup] = fields.ForeignKeyField(
        "models.Powerup", related_name="used_instances", null=False
    )
    used_at = fields.DatetimeField(auto_now_add=True)

Powerup_Pydantic = pydantic_model_creator(Powerup)
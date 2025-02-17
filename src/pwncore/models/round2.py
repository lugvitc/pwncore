from __future__ import annotations
from datetime import datetime, timezone
from tortoise import fields
from tortoise.models import Model
from tortoise.contrib.pydantic import pydantic_model_creator
from pwncore.models import (
    Problem
)
from pwncore.config import config, PowerUpType

__all__ = (
    "AttackDefProblem",
    "AttackDefTeam",
    "ActivatedPowerups"
)
#TODO: Actually implement this.
# For now this is a dummy class for testing AttackDefTeam.
class AttackDefProblem(Model):
    problem: fields.OneToOneRelation[Problem] = fields.OneToOneField(
        "models.Problem"
    )
    attack_def_team: fields.ForeignKeyRelation[AttackDefTeam] = fields.ForeignKeyField(
        "models.AttackDefTeam", related_name="assigned_attack_def_problem"
    )

class AttackDefTeam(Model):
    team: fields.OneToOneRelation[Team] = fields.OneToOneField(
        "models.Team", null=False
    )
    assigned_attack_def_problem: fields.ReverseRelation(AttackDefProblem)


class ActivatedPowerups(Model):
    id = fields.IntField(pk=True)
    used_by: fields.OneToOneRelation[AttackDefTeam] = fields.OneToOneField(
        "models.AttackDefTeam", related_name="powerups_used", null=False
    )
    used_on: fields.OneToOneNullableRelation[AttackDefTeam] = fields.OneToOneField(
        "models.AttackDefTeam", related_name="powerups_defended"
    )
    powerup_type = fields.data.CharEnumField(enum_type=PowerUpType, null=False)
    started_at = fields.data.DatetimeField(auto_now_add=True)

    def is_active(self) -> bool:
        duration = config.powerups[self.powerup_type]["duration"]
        if ((self.started_at + duration) < datetime.now(timezone.utc)):
            return False

        return True

    class PydanticMeta:
        arbitrary_types_allowed = True
        computed = ("is_active",)

ActivatedPowerups_Pydantic = pydantic_model_creator(ActivatedPowerups)
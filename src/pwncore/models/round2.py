from __future__ import annotations
from tortoise import fields
from tortoise.models import Model
from tortoise.expressions import F

__all__ = (
    "AttackDefProblem",
    "AttackDefTeam",
    "Problem",
    "Powerup",
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
    async def remaining_powerups(self):
        return self.powerups.filter(used_count__lt=F('max_uses'))

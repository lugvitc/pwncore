from __future__ import annotations
from tortoise import fields
from tortoise.models import Model
__all__ = (
    "AttackDefProblem",
    "AttackDefTeam",
    "Problem",
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

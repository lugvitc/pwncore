from tortoise import fields
from tortoise.models import Model
from tortoise.contrib.pydantic import pydantic_model_creator

from pwncore.models.ctf import Problem
from pwncore.models.user import Team


class AttackDefProblem(Model):
    id = fields.IntField(pk=True)
    team: fields.ForeignKeyRelation[Team] = fields.ForeignKeyField(
        "models.Team", related_name="attackdef_problems"
    )
    problem: fields.ForeignKeyRelation[Problem] = fields.ForeignKeyField(
        "models.Problem", related_name="problems"
    )


AttackDefProblem_Pydantic = pydantic_model_creator(AttackDefProblem)
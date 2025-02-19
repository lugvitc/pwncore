
from tortoise import fields
from tortoise.models import Model
from tortoise.contrib.pydantic import pydantic_model_creator

from ctf import Problem
from user import Team


class AttackDefProblem(Model):
    id = fields.IntField(pk=True)
    team: fields.ForeignKeyRelation[Team] = fields.ForeignKeyField(
        "models.Team", related_name="attackdef_problems"
    )
    problem: fields.ForeignKeyRelation[Problem] = fields.ForeignKeyField(
        "models.Problem", related_name="problems"
    )

    def __repr__(self):
        return (
            f"<AttackDefProblem id={self.id} problem_id={self.problem_id} team_id={self.team_id_}>" # team_id_ to access id via relation
        )


AttackDefProblem_Pydantic = pydantic_model_creator(AttackDefProblem)
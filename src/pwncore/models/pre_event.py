from __future__ import annotations

from tortoise.models import Model
from tortoise import fields
from tortoise.contrib.pydantic import pydantic_model_creator

from pwncore.models.ctf import BaseProblem

__all__ = ("PreEventSolvedProblem", "PreEventProblem", "PreEventProblem_Pydantic")


class PreEventProblem(BaseProblem):
    flag = fields.TextField()
    url = fields.TextField()  # Link to CTF file/repo/website

    date = fields.DateField()

    class PydanticMeta:
        exclude = ("flag",)


class PreEventSolvedProblem(Model):
    tag = fields.CharField(128)
    problem: fields.ForeignKeyRelation[PreEventProblem] = fields.ForeignKeyField(
        "models.PreEventProblem"
    )
    solved_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        unique_together = (("tag", "problem"),)


PreEventProblem_Pydantic = pydantic_model_creator(PreEventProblem)

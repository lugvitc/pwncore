from __future__ import annotations

from tortoise.models import Model
from tortoise import fields

from pwncore.models.ctf import BaseProblem

__all__ = (
    "PreEventSolvedProblem",
    "PreEventProblem",
)


class PreEventProblem(BaseProblem):
    flag = fields.TextField()
    url = fields.TextField()  # Link to CTF file/repo/website


class PreEventSolvedProblem(Model):
    tag = fields.CharField(128)
    problem: fields.ForeignKeyRelation[PreEventProblem] = fields.ForeignKeyField(
        "models.PreEventProblem"
    )
    solved_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        unique_together = (("tag", "problem"),)

from __future__ import annotations

from tortoise.models import Model
from tortoise import fields
from tortoise.contrib.pydantic import pydantic_model_creator

from pwncore.models.user import Team

__all__ = (
    "Problem",
    "Hint",
    "SolvedProblem",
    "ViewedHint",
    "Problem_Pydantic",
    "Hint_Pydantic",
)


class Problem(Model):
    name = fields.TextField()
    description = fields.TextField()
    points = fields.IntField()
    author = fields.TextField()

    image_name = fields.TextField()
    image_config: fields.Field[dict[str, list]] = fields.JSONField()  # type: ignore[assignment]

    hints: fields.ReverseRelation[Hint]


class Hint(Model):
    id = fields.IntField(pk=True)
    order = fields.SmallIntField()  # 0, 1, 2
    problem: fields.ForeignKeyRelation[Problem] = fields.ForeignKeyField(
        "models.Problem"
    )
    text = fields.TextField()

    class Meta:
        ordering = ("order",)


class SolvedProblem(Model):
    team: fields.ForeignKeyRelation[Team] = fields.ForeignKeyField("models.Team")
    problem: fields.ForeignKeyRelation[Problem] = fields.ForeignKeyField(
        "models.Problem", related_name="problem"
    )
    solved_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        unique_together = (("team", "problem"),)


class ViewedHint(Model):
    team: fields.ForeignKeyRelation[Team] = fields.ForeignKeyField("models.Team")
    hint: fields.ForeignKeyRelation[Hint] = fields.ForeignKeyField(
        "models.Hint",
        # related_name="viewed_hint"
    )

    class Meta:
        unique_together = (("team", "hint"),)


Problem_Pydantic = pydantic_model_creator(Problem)
Hint_Pydantic = pydantic_model_creator(Hint)

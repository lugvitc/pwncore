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
    "BaseProblem_Pydantic",
    "Hint_Pydantic",
)


class BaseProblem(Model):
    name = fields.TextField()
    description = fields.TextField()
    # both tables inherit points, for pre-event points means coins
    points = fields.IntField()
    author = fields.TextField()


class Problem(BaseProblem):
    image_name = fields.TextField()
    image_config: fields.Field[dict[str, list]] = fields.JSONField(
        null=True
    )  # type: ignore[assignment]

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
        "models.Problem"
    )
    solved_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        unique_together = (("team", "problem"),)


class ViewedHint(Model):
    team: fields.ForeignKeyRelation[Team] = fields.ForeignKeyField("models.Team")
    hint: fields.ForeignKeyRelation[Hint] = fields.ForeignKeyField(
        "models.Hint",
    )

    class Meta:
        unique_together = (("team", "hint"),)


BaseProblem_Pydantic = pydantic_model_creator(BaseProblem)
Hint_Pydantic = pydantic_model_creator(Hint)

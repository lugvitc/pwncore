from __future__ import annotations

from typing import TYPE_CHECKING

from tortoise.models import Model
from tortoise import fields
from tortoise.contrib.pydantic import pydantic_model_creator

if TYPE_CHECKING:
    from tortoise.fields import Field
    from pwncore.models.user import Team

__all__ = ("Problem", "Hint", "SolvedProblem", "ViewedHint")


class Problem(Model):
    name = fields.TextField()
    description = fields.TextField()
    points = fields.IntField()
    author = fields.TextField()

    image_name = fields.TextField()
    image_config: fields.Field[dict[str, list]] = fields.JSONField()  # type: ignore[assignment]

    hints: fields.ReverseRelation[Hint]


# Problem_Pydantic = pydantic_model_creator(Problem, name="Problem")
# ProblemIn_Pydantic = pydantic_model_creator(Problem, name="ProblemIn", exclude_readonly=True)

class Hint(Model):
    order = fields.SmallIntField()  # 0, 1, 2
    problem: fields.ForeignKeyRelation[Problem] = fields.ForeignKeyField(
        "models.Problem", related_name="hints"
    )
    text = fields.TextField()

    class Meta:
        ordering = ("order",)

Hint_Pydantic = pydantic_model_creator(Hint, name="Hint")
HintIn_Pydantic = pydantic_model_creator(Hint, name="HintIn", exclude_readonly=True)

class SolvedProblem(Model):
    team: fields.ForeignKeyRelation[Team] = fields.ForeignKeyField("models.Team")
    problem: fields.ForeignKeyRelation[Problem] = fields.ForeignKeyField(
        "models.Problem"
    )
    solved_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        unique_together = (("team", "problem"),)

SolvedProblem_Pydantic = pydantic_model_creator(SolvedProblem, name="SolvedProblem")
SolvedProblemIn_Pydantic = pydantic_model_creator(SolvedProblem, name="SolvedProblemIn", exclude_readonly=True)


class ViewedHint(Model):
    team: fields.ForeignKeyRelation[Team] = fields.ForeignKeyField("models.Team")
    hint: fields.ForeignKeyRelation[Hint] = fields.ForeignKeyField("models.Hint")

    class Meta:
        unique_together = (("team", "hint"),)

ViewedHint_Pydantic = pydantic_model_creator(ViewedHint, name="ViewedHint")
ViewedHintIn_Pydantic = pydantic_model_creator(ViewedHint, name="ViewedHintIn", exclude_readonly=True)



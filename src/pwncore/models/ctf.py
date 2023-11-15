from __future__ import annotations

from typing import TYPE_CHECKING

from tortoise.models import Model
from tortoise import fields

if TYPE_CHECKING:
    from tortoise.fields import Field
    from pwncore.models.user import Team

__all__ = ("Problem", "Hint", "Image", "SolvedProblem", "ViewedHint")


class Problem(Model):
    name = fields.TextField()
    description = fields.TextField()
    points = fields.IntField()
    author = fields.TextField()

    hints: fields.ReverseRelation[Hint]
    image: fields.OneToOneRelation[Image]


class Hint(Model):
    order = fields.SmallIntField()  # 0, 1, 2
    problem: fields.ForeignKeyRelation[Problem] = fields.ForeignKeyField(
        "models.Problem", related_name="hints"
    )
    text = fields.TextField()

    class Meta:
        ordering = ("hint_order",)


class Image(Model):
    name = fields.TextField()
    config: Field[dict[str, list]] = fields.JSONField()  # type: ignore[assignment]
    problem: fields.OneToOneRelation[Problem] = fields.OneToOneField(
        "models.Problem", related_name="image"
    )


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
    hint: fields.ForeignKeyRelation[Hint] = fields.ForeignKeyField("models.Hint")

    class Meta:
        unique_together = (("team", "hint"),)

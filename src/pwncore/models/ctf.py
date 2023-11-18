from __future__ import annotations

from typing import TYPE_CHECKING

from tortoise.models import Model
from tortoise import fields

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
    image_config: Field[dict[str, list]] = fields.JSONField()  # type: ignore[assignment]

    hints: fields.ReverseRelation[Hint]


class Hint(Model):
    order = fields.SmallIntField()  # 0, 1, 2
    problem: fields.ForeignKeyRelation[Problem] = fields.ForeignKeyField(
        "models.Problem", related_name="hints"
    )
    text = fields.TextField()

    class Meta:
        ordering = ("order",)

    async def return_hint(problem_id: int, team_id: int):
        viewed = await ViewedHint.filter(team_id=team_id).values_list(
            "hint_id", flat=True
        )
        if viewed:
            viewed_hint = await Hint.filter(
                problem_id=problem_id, id__in=viewed
            ).values_list("order", flat=True)
            hint = await Hint.get_or_none(
                problem_id=problem_id, order=max(viewed_hint) + 1
            ).values()
        else:
            hint = await Hint.get(problem_id=problem_id, order=0).values()

        if hint:
            await ViewedHint.create(hint_id=hint["id"], team_id=team_id)
        return hint


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
        "models.Hint", related_name="hints"
    )

    class Meta:
        unique_together = (("team", "hint"),)

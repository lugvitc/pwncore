from __future__ import annotations

from time import monotonic

from fastapi import APIRouter, Request

from tortoise.expressions import RawSQL, Q

from pwncore.models import Team

# Metadata at the top for instant accessibility
metadata = {"name": "leaderboard", "description": "Operations on the leaderboard"}

router = APIRouter(prefix="/leaderboard", tags=["leaderboard"])


class ExpiringLBCache:
    period: float
    last_update: float
    data: list[dict[str, float]]

    def __init__(self, period: float) -> None:
        self.period = period
        self.last_update = 0
        self.data = []

    async def _do_update(self):
        self.data = (
            await Team.all()
            .filter(Q(solved_problem__problem__visible=True) | Q(points__gte=0))
            .annotate(
                tpoints=RawSQL(
                    'COALESCE((SUM("solvedproblem"."penalty" * '
                    '"solvedproblem__problem"."points")'
                    ' + "team"."points"), 0)'
                )
            )
            .group_by("id", "meta_team__name")
            .order_by("-tpoints")
            .values("name", "tpoints", "meta_team__name")
        )

        self.last_update = monotonic()

    async def get_lb(self, req: Request):
        if (
            getattr(req.app.state, "force_expire", False)
            or (monotonic() - self.last_update) > self.period  # noqa: W503
        ):
            await self._do_update()
            req.app.state.force_expire = False
        return self.data


gcache = ExpiringLBCache(30.0)


@router.get("")
async def fetch_leaderboard(req: Request):
    return await gcache.get_lb(req)

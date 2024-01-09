from __future__ import annotations
from fastapi import APIRouter
from tortoise.functions import Sum

from pwncore.models import SolvedProblem, Team

# Metadata at the top for instant accessibility
metadata = {"name": "leaderboard", "description": "Operations on the leaderboard"}

router = APIRouter(prefix="/leaderboard", tags=["leaderboard"])


@router.get("")
async def fetch_leaderboard():
    points = (
        await Team.all()
        .annotate(team_points=Sum("solved_problem__problem__points"))
        .values_list("name", "team_points")
    )
    points = sorted(points, key=lambda x: x[0], reverse=True)
    return points

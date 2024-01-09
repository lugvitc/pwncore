from __future__ import annotations
from fastapi import APIRouter

from pwncore.models import SolvedProblem, Team

# Metadata at the top for instant accessibility
metadata = {"name": "leaderboard", "description": "Operations on the leaderboard"}

router = APIRouter(prefix="/leaderboard", tags=["leaderboard"])


@router.get("")
async def fetch_leaderboard():
    teams = await Team.all()
    leaderboard = {}
    for team in teams:
        problems_solved_by_team = await SolvedProblem.filter(
            team__id=team.id
        ).values_list("problem__points", flat=True)
        # Tortoise's return type is List[Tuples] even after flat=True makes it List[]
        # Hence ignore:
        leaderboard[team.name] = sum(problems_solved_by_team)  # type: ignore[arg-type]

    # Uncomment to return sorted leaderboard
    # leaderboard = dict(sorted(leaderboard.items(), key=lambda x: x[0], reverse=True))
    return leaderboard

from __future__ import annotations
from fastapi import APIRouter

from pwncore.models import SolvedProblem, Team, Team_Pydantic

# Metadata at the top for instant accessibility
metadata = {"name": "leaderboard", "description": "Operations on the leaderboard"}

router = APIRouter(prefix="/leaderboard", tags=["leaderboard"])


@router.get("/")
async def fetch_leaderboard():
    teams = await Team_Pydantic.from_queryset(Team.all())
    # points = await SolvedProblem.filter(team=2).values("problem__points")
    leaderboard = {}
    for team in teams:
        problems_solved_by_team = await SolvedProblem.filter(
            team__id=team.id
        ).values_list("problem__points", flat=True)
        leaderboard[team.name] = sum(problems_solved_by_team)
    # Uncomment to return sorted leaderboard
    # leaderboard = dict(sorted(leaderboard.items(), key=lambda x: x[0], reverse=True))
    return leaderboard

from pydantic import BaseModel

# defining Pydantic response model
class LeaderboardEntry(BaseModel):
    """
    Returns the leaderboard entry for a team.
    name: team name
    tpoints: total points
    """
    name: str
    tpoints: int
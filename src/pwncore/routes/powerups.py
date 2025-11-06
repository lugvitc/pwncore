#based on the issue #69
from pwncore.config import config, powerups
from pwncore.types import PowerUpType

async def upgrade_question(question, team):
    
    upgrade_cost = powerups[PowerUpType.UPGRADE]["cost"]
    
    
    if question.difficulty_level >= config.max_difficulty:
        raise Exception("Question difficulty is already at maximum.")
    
    if team.points < upgrade_cost:
        raise Exception("Insufficient points to upgrade.")
    

    question.difficulty_level += 1
    team.points -= upgrade_cost

    await question.save()
    await team.save()

    return {
        "status": "success",
        "new_difficulty": question.difficulty,
        "remaining_points": team.points
    }

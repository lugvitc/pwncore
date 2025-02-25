from fastapi import APIRouter, Response
from tortoise.transactions import in_transaction

import pwncore.containerASD as containerASD
from pwncore.config import config
from pwncore.models import Team, Team_Pydantic, Problem, Container

router = APIRouter(prefix="/admin/dashboard", tags=["admin-dashboard"])

@router.get("/teams", summary="List all teams", description="Returns a list of all teams stored in the database. *Markdown* supported.")
async def list_teams():
    '''
    This route fetches all teams via Team_Pydantic.from_queryset,
    allowing admins to see each team's general details.
    '''
    return await Team_Pydantic.from_queryset(Team.all())

@router.post("/toggle_problem/{problem_id}",
    summary="Toggle problem visibility",
    description="Allow admins to show/hide a problem. *Markdown* supported."
)
async def toggle_problem_visibility(problem_id: int, response: Response):
    '''
    Toggles a problem\'s `visible` flag. If the problem
    is currently visible, this will hide it, and vice versa.
    '''
    async with in_transaction():
        prob = await Problem.get_or_none(id=problem_id)
        if not prob:
            response.status_code = 404
            return {"msg_code": config.msg_codes["ctf_not_found"]}
        prob.visible = not prob.visible
        await prob.save()
    return {"visible": prob.visible}

@router.post("/stop_container/{docker_id}")
async def stop_container(docker_id: str, response: Response):
    '''
    Stops and removes a running container identified by its Docker ID,
    deleting the container record from the database.
    
    Markdown is supported here as well.
    '''
    async with in_transaction():
        container_rec = await Container.get_or_none(docker_id=docker_id)
        if not container_rec:
            response.status_code = 404
            return {"msg_code": "container_not_found"}
        try:
            container = await containerASD.docker_client.containers.get(docker_id)
            await container.kill()
            await container.delete()
            await container_rec.delete()
        except Exception:
            response.status_code = 500
            return {"msg_code": config.msg_codes["db_error"]}
    return {"status": "stopped"}

@router.post("/adjust_coins/{team_id}")
async def adjust_team_coins(team_id: int, delta: int, response: Response):
    '''
    Modifies a team's coin total by adding the given delta (can be negative or positive).
    Returns the updated coin balance.
    '''
    async with in_transaction():
        team = await Team.get_or_none(id=team_id)
        if not team:
            response.status_code = 404
            return {"msg_code": config.msg_codes["team_not_found"]}
        team.coins += delta
        await team.save()
    return {"coins": team.coins}

@router.get("/team_info/{team_id}")
async def get_team_details(team_id: int, response: Response):
    '''
    Fetches detailed info about a specific team, including its name,
    coins, points, and a list of members (by tag and name).
    '''
    team = await Team.get_or_none(id=team_id).prefetch_related("members")
    if not team:
        response.status_code = 404
        return {"msg_code": config.msg_codes["team_not_found"]}
    members = [{"tag": u.tag, "name": u.name} for u in team.members]  # type: ignore
    return {
        "id": team.id,
        "name": team.name,
        "coins": team.coins,
        "points": team.points,
        "members": members,
    }
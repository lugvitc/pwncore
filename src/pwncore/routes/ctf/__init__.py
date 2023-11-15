from __future__ import annotations

from fastapi import APIRouter

# Metadata at the top for instant accessibility
metadata = {
    "name": "ctf",
    "description": "Operations related to CTF, except"
    "create and delete (those are under admin)",
}

router = APIRouter(prefix="/ctf", tags=["ctf"])

# Routes that do not need a separate submodule for themselves


@router.get("/list")
async def ctf_list():
    # Get list of ctfs
    return [
        {"name": "Password Juggling", "ctf_id": 2243},
        {"name": "hexane", "ctf_id": 2242},
    ]


@router.get("/{ctf_id}")
async def ctf_get(ctf_id: int):
    # Get ctf from ctf_id
    return {"status": "logged in!"}


@router.get("/flag/{ctf_id}")
async def flag(ctf_id: int):
    # compare flag against database
    return {"status": True}


@router.get("/hint/{ctf_id}")
async def hint(ctf_id: int):
    # fetch hint
    # reduce points
    return {"hint": "Ask the cat, it was there when it was hidden", "points": 144}

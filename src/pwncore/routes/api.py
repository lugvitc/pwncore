from fastapi import APIRouter

router = APIRouter(prefix="/api/ctf", tags=["flag"])


@router.get("/view/{ctf_id}")
async def view(ctf_id: int):
    # fetch ctf
    return {"ctf_name": "Key Verifier", "author": "mradigen", "container": "127.0.0.1:8000"}


@router.get("/flag/{ctf_id}")
async def flag(ctf_id: int):
    # compare flag against database
    return {"status": True}


@router.get("/hint/{ctf_id}")
async def hint(ctf_id: int):
    # fetch hint
    # reduce points
    return {"hint": "Ask the cat, it was there when it was hidden", "points": 144}

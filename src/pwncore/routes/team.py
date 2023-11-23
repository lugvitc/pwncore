from __future__ import annotations

from fastapi import APIRouter

# Metadata at the top for instant accessibility
metadata = {"name": "team", "description": "Operations with teams"}

router = APIRouter(prefix="/team", tags=["team"])

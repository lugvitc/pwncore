from __future__ import annotations

import jwt
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from tortoise.contrib.pydantic import pydantic_model_creator
from pwncore.models import User, Team
from pwncore.config import config
import datetime
from passlib.hash import bcrypt

# Metadata at the top for instant accessibility
metadata = {"name": "team", "description": "Operations with teams"}

router = APIRouter(prefix="/team", tags=["team"])

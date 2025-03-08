from pydantic import BaseModel
import typing as t

# defining Pydantic response models
class AuthBody(BaseModel):
    """
    Request body for login
    name: name of the user
    password: password of the user
    """
    name: str
    password: str


class SignupBody(BaseModel):
    name: str
    password: str
    tags: set[str]


# Response Models
class SignupResponse(BaseModel):
    """
    msg_code: 13 (signup_success)
    """
    msg_code: t.Literal[13]

class SignupErrorUsersNotFound(BaseModel):
    """
    msg_code: 24 (users_not_found)
    tags: list[str]
    """
    msg_code: t.Literal[24]
    tags: list[str]

class SignupErrorUsersInTeam(BaseModel):
    """
    msg_code: 20 (user_already_in_team)
    tags: list[str]
    """
    msg_code: t.Literal[20]
    tags: list[str]

class LoginResponse(BaseModel):
    """
    msg_code: 15 (login_success)
    access_token: JWT access token
    token_type: "bearer"
    """
    msg_code: t.Literal[15]
    access_token: str
    token_type: str

class Auth_ErrorResponse(BaseModel):
    """
    msg_code can be:
    0 (db_error)
    17 (team_exists)
    10 (team_not_found)
    14 (wrong_password)
    """
    msg_code: t.Literal[0, 17, 10, 14]

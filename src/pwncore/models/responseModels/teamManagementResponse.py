from pydantic import BaseModel
import typing as t


class UserAddBody(BaseModel):
    """
    Request body for adding a user
    """
    tag: str
    name: str
    email: str
    phone_num: str


class UserRemoveBody(BaseModel):
    """
    Request body for removing a user
    """
    tag: str

class MemberStatusResponse(BaseModel):
    """
    Response for user management operations in teams
    msg_code for response:
    - (success) 
        - user_added: 18
        - user_removed: 19

    - (fail) 
        - user_already_in_team: 20
        - user_not_in_team : 21
        - db_error: 0
    """
    msg_code: int
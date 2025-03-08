from pydantic import BaseModel
import typing as t

class UserAddBody(BaseModel):
    """
    Request body for adding a user
    tag: team tag
    name: name of the user
    email: email of the user
    phone_num: phone number of the user
    """
    tag: str
    name: str
    email: str
    phone_num: str


class UserRemoveBody(BaseModel):
    """
    Request body for removing a user
    tag: team tag
    """
    tag: str


class MessageResponse(BaseModel):
    """
    Response for user management operations
    msg_code: message code
    """
    msg_code: int
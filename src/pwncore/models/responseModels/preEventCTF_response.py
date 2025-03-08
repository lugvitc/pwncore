from pydantic import BaseModel

# pydantic response models 
class PreEventFlag(BaseModel):
    """
    Response for pre-event flag submission
    tag: team tag
    flag: flag submitted
    email: email of the team
    """
    tag: str
    flag: str
    email: str


class CoinsQuery(BaseModel):
    """
    Response for pre-event coins query
    tag: team tag
    """
    tag: str

class CoinsResponse(BaseModel):
    """
    Response for pre-event coins query
    coins: total coins earned by the team in pre-event CTFs
    """
    coins: int

class FlagSubmissionResponse(BaseModel):
    """
    Response for pre-event flag submission
    status: bool
    coins: total coins earned by the team in pre-event CTFs
    """
    status: bool
    coins: int

class preEventCTF_ErrorResponse(BaseModel):
    msg_code: int

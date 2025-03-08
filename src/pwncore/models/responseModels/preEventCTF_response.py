from pydantic import BaseModel

# pydantic response models 
class PreEventFlag(BaseModel):
    """
    Response for pre-event flag submission
    """
    tag: str
    flag: str
    email: str


class CoinsQuery(BaseModel):
    """
    Response for pre-event coins query
    """
    tag: str

class CoinsResponse(BaseModel):
    """
    Response for pre-event coins query
    """
    coins: int

class FlagSubmissionResponse(BaseModel):
    """
    Response for pre-event flag submission
    """
    status: bool
    coins: int

class preEventCTF_ErrorResponse(BaseModel):
    msg_code: int

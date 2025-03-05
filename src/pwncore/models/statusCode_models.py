from pydantic import BaseModel
from typing import List, Optional

class ErrorResponse(BaseModel):
    """
    Generic error response
    msg_code: 0 (db_error), 2 (ctf_not_found)
    """
    msg_code: int

class ContainerStartResponse(BaseModel):
    """
    Response for container start operation
    msg_code: 3 (success), 7 (already running), 8 (limit reached), 0 (db_error)
    """
    msg_code: int
    ports: Optional[List[int]] = None
    ctf_id: Optional[int] = None

class ContainerStopResponse(BaseModel):
    """
    Response for container stop operations
    msg_code: 4 (stop success), 5 (stopall success), 6 (not found), 0 (db_error)
    """
    msg_code: int

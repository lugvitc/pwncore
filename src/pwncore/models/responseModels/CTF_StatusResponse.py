from pydantic import BaseModel
from typing import List, Optional

class CTF_ErrorResponse(BaseModel):
    """
    Error response for CTF operations
    - 404: ctf_not_found : 2
    - 403: hint_limit_reached : 9
    - 412: Insufficient coins : 22
    - 406: container_already_running : 7
    - 429: container_limit_reached : 8
    - 500: db_error : 0
    """
    msg_code: int

class ContainerStartResponse(BaseModel):
    """
    Response for container start operation
    msg_codes: 
    - (success) container_start : 3
    """
    msg_code: int
    ports: Optional[List[int]] = None
    ctf_id: Optional[int] = None

class ContainerStopResponse(BaseModel):
    """
    Response for container stop operations
    - (success) container_stop : 4
    - (fail) 
        - 404: ctf_not_found : 2
        - 400: container_not_found  : 6
        - 500: db_error : 0 
    """
    msg_code: int

class ContainerPortsResponse(BaseModel):
    """
    Response for all open ports of containers
    """
    ports: dict[int, list[int]]
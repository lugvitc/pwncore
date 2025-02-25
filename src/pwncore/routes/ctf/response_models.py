from pydantic import BaseModel, Field
from typing import List, Literal

class ContainerStartResponse(BaseModel):
    """Pydantic Response model for container start operation
    
    Message codes:
    - 3: Container started successfully
    - 7: Container already running
    - 8: Container limit reached
    """
    msg_code: Literal[3, 7, 8] = Field(
        description="Status code indicating operation result: 3=success, 7=already running, 8=limit reached"
    )
    ports: List[int] = Field(
        default=None, 
        description="List of mapped container ports"
    )
    ctf_id: int = Field(
        default=None,
        description="ID of the CTF challenge"
    )

class ContainerStopResponse(BaseModel):
    """Pydantic Response model for container stop operations
    
    Message codes:
    - 4: Container stopped successfully 
    - 5: All team containers stopped successfully
    """
    msg_code: Literal[4, 5] = Field(
        description="Status code indicating operation result: 4=single stop, 5=stop all"
    )

class ErrorResponse(BaseModel):
    """Pydantic Error response model
    
    Message codes:
    - 0: Database error
    - 2: CTF not found
    - 6: Container not found
    """
    msg_code: Literal[0, 2, 6] = Field(
        description="Error code: 0=DB error, 2=CTF not found, 6=container not found"
    )

    class Config:
        schema_extra = {
            "examples": [
                {
                    "msg_code": 0,
                    "description": "Database error occurred"
                },
                {
                    "msg_code": 2,
                    "description": "CTF challenge not found"
                },
                {
                    "msg_code": 6,
                    "description": "Container not found"
                }
            ]
        }

from pydantic import BaseModel
from typing import Optional

class AdminBaseResponse(BaseModel):
    """
    Generic response for admin operations
    """
    success: bool
    message: Optional[str] = None
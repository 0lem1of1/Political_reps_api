from pydantic import BaseModel
from typing import List, Optional

class RepresentativeDetail(BaseModel):
    name: str
    title: str
    branch: Optional[str] = None

    class Config:
        from_attributes = True

class APIResponse(BaseModel):
    zip: str
    representatives: List[RepresentativeDetail]


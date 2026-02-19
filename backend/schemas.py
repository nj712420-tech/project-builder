# schemas.py
from pydantic import BaseModel

class ProjectRequest(BaseModel):
    prompt: str
    include_db: bool = False
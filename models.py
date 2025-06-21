from pydantic import BaseModel
from typing import Optional

class Reference(BaseModel):
    id: int
    title: Optional[str] = None
    author: Optional[str] = None
    year: Optional[str] = None
    journal: Optional[str] = None # Corresponds to secondary_title
    abstract: Optional[str] = None
    filepath: Optional[str] = None # Relative path from the .Data folder

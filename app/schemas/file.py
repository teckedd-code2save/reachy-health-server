from pydantic import BaseModel
from typing import Optional

class FileResponse(BaseModel):
    filename: str
    url: str
    content_type: Optional[str] = None
    size: Optional[int] = None
    created_at: Optional[str] = None 
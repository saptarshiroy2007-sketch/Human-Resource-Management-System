from datetime import datetime

from pydantic import BaseModel


class DocumentOut(BaseModel):
    id: int
    user_id: int
    doc_type: str
    file_url: str
    uploaded_at: datetime

    model_config = {"from_attributes": True}

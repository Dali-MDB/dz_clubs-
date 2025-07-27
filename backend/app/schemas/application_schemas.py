from pydantic import BaseModel
from datetime import datetime
from app.models.events_model import application_status
from app.schemas.response_schemas import ResponseDisplay
from typing import List,ClassVar


class ApplicationBase(BaseModel):
    motivation : str


class ApplicationCreate(ApplicationBase):
    pass

class ApplicationUpdate(ApplicationBase):
    motivation : str|None=None

class ApplicationDisplay(ApplicationBase):
    id : int
    user_id : int|None = None
    submitted_at : datetime
    event_id : int
    status : application_status
    responses: List[ResponseDisplay] = []

    class Config:
        from_attributes = True

class Application(ApplicationBase):
    id : int
    user_id : int 
    submitted_at : datetime
    event_id : int
    status : application_status

    class Config:
        from_attributes = True


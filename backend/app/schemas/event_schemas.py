from pydantic import BaseModel
from datetime import datetime
from app.models.events_model import event_types,event_status


class EventBase(BaseModel):
    name : str
    date_start : datetime
    date_end : datetime
    venue : str
    description : str
    event_type : event_types
    content : str
    sheet : str

class EventCreate(EventBase):
    pass

class EventDisplay(EventBase):
    id : int
    club_id : int
    club_name : str
    image_url : str | None = None

class EventUpdate(EventBase):
    name : str | None = None
    date_start : datetime | None = None
    date_end : datetime | None = None
    venue : str | None = None
    description : str | None = None
    event_type : event_types | None = None
    content : str | None = None
    sheet : str     | None = None



class Event(EventBase):
    id : int
    club_id : int
    image_url : str | None = None
    class Config:
        from_attributes = True

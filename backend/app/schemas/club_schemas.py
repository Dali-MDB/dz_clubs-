from pydantic import BaseModel, Field
from typing import List
from .user_schemas import User,UserDisplay



class ClubBase(BaseModel):
    name : str
    university : str
    address : str
    description : str
    phone : str


class ClubCreate(ClubBase):
    pass

class ClubDisplay(ClubBase):
    id : int
    user_id : int
    image_url : str | None = None

    user : UserDisplay

    class Config:
        from_attributes = True


class ClubUpdate(ClubBase):
    name : str | None = None
    university : str | None = None
    address : str | None = None
    description : str | None = None
    phone : str | None = None


class Club(ClubBase):
    id : int
    user_id : int
    image_url : str | None = None
    user : User

    class Config:
        from_attributes = True
    
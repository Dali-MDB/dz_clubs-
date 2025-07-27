from pydantic import BaseModel,Field
from typing import List
from .user_schemas import UserDisplay,User


class PersonBase(BaseModel):
    full_name : str
    university : str
    phone : str
    major : str
    year : int = Field(ge=1,le=5)
    city : str



class PersonCreate(PersonBase):
    pass  

class PersonDisplay(PersonBase):
    id : int
    user_id : int
    user : UserDisplay
    image_url : str | None = None
    class Config:
        from_attributes = True



class PersonUpdate(PersonBase):
    full_name : str | None
    university : str | None
    phone : str | None
    major : str | None
    year : int | None
    city : str | None


class Person(PersonBase):
    id : int
    user_id : int
    user : User
    image_url : str | None = None
    class Config:
        from_attributes = True




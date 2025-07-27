from pydantic import BaseModel,Field,EmailStr
from typing import Annotated,List
from app.models.users_model import user_types





class UserBase(BaseModel):
    email : EmailStr 


class UserCreate(UserBase):
    password : str


class UserDisplay(UserBase):
    id : int
    user_type : user_types

    class Config:
        from_attributes = True


class UserUpdate(UserBase):
    email : EmailStr | None 
    

class User(UserBase):
    id : int
    password : str
    user_type : user_types

    class Config:
        from_attributes = True

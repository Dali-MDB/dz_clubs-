from pydantic import BaseModel
from app.models.events_model import question_types
from typing import List



class QuestionBase(BaseModel):
    text:str
    question_type:question_types
    is_required:bool
    options: str | None = None



class QuestionCreate(QuestionBase):
    pass

class QuestionDisplay(QuestionBase):
    id:int
    event_id:int

class QuestionUpdate(QuestionBase):
    text: str | None = None
    question_type: question_types | None = None
    is_required: bool | None = None
    options: str | None = None



class Question(QuestionBase):
    id:int
    event_id:int
    

    class Config:
        from_attributes = True






from pydantic import BaseModel



class ResponseBase(BaseModel):
    answer:str



class ResponseCreate(ResponseBase):
    question_id:int

class ResponseDisplay(ResponseBase):
    id:int
    question_id:int
    application_id:int
    question_text : str

    class Config:
        from_attributes = True


class ResponseUpdate(ResponseBase):
    answer : str|None=None


class Respone(ResponseBase):
    id:int
    question_id:int
    application_id:int
    answer:str

    class Config:
        from_attributes = True



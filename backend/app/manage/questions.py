from fastapi import APIRouter,Depends,status
from app.schemas.question_schemas import QuestionDisplay,QuestionCreate,QuestionUpdate
from app.dependecies import sessionDep,Session
from app.manage.events import retrieve_event
from app.manage.autheticaton import oauth2_scheme,get_current_user
from typing import Annotated
from fastapi.exceptions import HTTPException
from app.models.events_model import  Question

question_router = APIRouter(prefix='/questions')




@question_router.post('/add_question/{event_id}/',response_model=QuestionDisplay)
def add_question(event_id:int,question:QuestionCreate,db:sessionDep,token:Annotated[str,Depends(oauth2_scheme)]):
    event = retrieve_event(event_id,db)
    user = get_current_user(token,db)
    #check permissions
    if user.user_type == 'PERSON' or user.club.id != event.club_id:
        raise HTTPException(status.HTTP_403_FORBIDDEN,'you are not alloed to do thisaction')
    question_data = question.model_dump()
    question_data['event_id'] = event_id
    question_db = Question(**question_data)
    db.add(question_db)
    db.commit()
    db.refresh(question_db)
    return question_db



@question_router.post('/add_question/{event_id}/mass_add/',response_model=dict[str,list[int]])
def add_question_mass(event_id:int,questions:list[QuestionCreate],db:sessionDep,token:Annotated[str,Depends(oauth2_scheme)]):
    event = retrieve_event(event_id,db)
    user = get_current_user(token,db)
    #check permissions
    if user.user_type == 'PERSON' or user.club.id != event.club_id:
        raise HTTPException(status.HTTP_403_FORBIDDEN,'you are not alloed to do thisaction')
    created_ids = []
    for question in questions:
        question_data = question.model_dump()
        question_data['event_id'] = event_id
        question_db = Question(**question_data)
        db.add(question_db)
        db.flush()    #assign id before commiting
        created_ids.append(question_db.id)

    db.commit()
    return {'questions_ids':created_ids}



def retrieve_question(question_id:int,db:Session):
    qst = db.query(Question).filter(Question.id == question_id).first()
    if not qst:
        raise HTTPException(404,'this question does not exist')
    return qst

@question_router.get('/get_question/{question_id}/',response_model=QuestionDisplay)
def get_question(question_id:int,db:sessionDep):
    return retrieve_question(question_id,db)


@question_router.put('/edit_question/{question_id}/',response_model=QuestionDisplay)
def edit_question(question_id:int,question:QuestionUpdate,token:Annotated[str,Depends(oauth2_scheme)],db:sessionDep):
    question_db = retrieve_question(question_id,db)
    user = get_current_user(token,db)
    if user.user_type == 'PERSON' or question_db.event.club_id != user.club.id:
        raise HTTPException(403,'you are not allowed to do this action')
    question_data = question.model_dump(exclude_unset=True)
    for key,val in question_data.items():
        setattr(question_db,key,val)
    db.commit()
    db.refresh(question_db)
    return question_db


@question_router.delete('/delete_question/{question_id}/')
def delete_question(question_id:int,token:Annotated[str,Depends(oauth2_scheme)],db:sessionDep):
    question_db = retrieve_question(question_id,db)
    user = get_current_user(token,db)
    if user.user_type == 'PERSON' or question_db.event.club_id != user.club.id:
        raise HTTPException(403,'you are not allowed to do this action')
    db.delete(question_db)
    db.commit()
    return {'details':'the question has been deleted successfully'}




@question_router.get('/get_event_questions/{event_id}/',response_model=list[QuestionDisplay])
def get_event_questions(event_id:int,db:sessionDep):
    return db.query(Question).filter(Question.event_id == event_id)


    




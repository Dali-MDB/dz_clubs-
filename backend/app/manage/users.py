from fastapi import Depends, APIRouter, HTTPException, status
from app.dependecies import sessionDep, Session
from app.models.users_model import Person
from app.models.events_model import Application
from app.schemas.person_schemas import PersonDisplay, PersonUpdate
from app.schemas.application_schemas import ApplicationDisplay
from app.manage.autheticaton import get_current_user, oauth2_scheme
from typing import Annotated
from sqlalchemy import desc
from fastapi import UploadFile, File
import os
import uuid
from fastapi.responses import FileResponse

user_router = APIRouter(prefix='/users')

def retrieve_person(person_id: int, db: Session):
    person = db.query(Person).filter(Person.id == person_id).first()
    if not person:
        raise HTTPException(status_code=404, detail='Person not found')
    return person

@user_router.get('/view_person/{person_id}/', response_model=PersonDisplay)
def view_person(person_id: int, db: sessionDep):
    person = retrieve_person(person_id, db)
    return person

@user_router.put('/edit_person/{person_id}/', response_model=PersonDisplay)
def edit_person(person_id: int, person_update: PersonUpdate, token: Annotated[str, Depends(oauth2_scheme)], db: sessionDep):
    person_db = retrieve_person(person_id, db)
    user = get_current_user(token, db)
    if user.user_type != 'PERSON' or user.person.id != person_db.id:
        raise HTTPException(status_code=403, detail='You are not allowed to edit this profile')
    person_data = person_update.model_dump(exclude_unset=True)
    for field, value in person_data.items():
        setattr(person_db, field, value)
    db.commit()
    db.refresh(person_db)
    return person_db

@user_router.delete('/delete_person/{person_id}/')
def delete_person(person_id: int, token: Annotated[str, Depends(oauth2_scheme)], db: sessionDep):
    person_db = retrieve_person(person_id, db)
    user = get_current_user(token, db)
    if user.user_type != 'PERSON' or user.person.id != person_db.id:
        raise HTTPException(status_code=403, detail='You are not allowed to delete this profile')
    # delete all applications associated with the person
    db.query(Application).filter(Application.user_id == person_id).delete()
    db.delete(person_db)
    db.commit()
    return {'details': 'Person deleted successfully'}

@user_router.get('/my_profile/', response_model=PersonDisplay)
def get_my_profile(token: Annotated[str, Depends(oauth2_scheme)], db: sessionDep):
    user = get_current_user(token, db)
    if user.user_type != 'PERSON':
        raise HTTPException(status_code=403, detail='You are not allowed to view this profile')
    return user.person

@user_router.get('/get_person_applications/self/', response_model=list[ApplicationDisplay])
def get_person_applications(token: Annotated[str, Depends(oauth2_scheme)], db: sessionDep):
    user = get_current_user(token, db)
    if user.user_type != 'PERSON':
        raise HTTPException(status_code=403, detail='You are not allowed to get applications')
    applications = db.query(Application).filter(Application.user_id == user.person.id).order_by(desc(Application.submitted_at)).all()
    return applications






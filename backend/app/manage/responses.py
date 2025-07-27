from fastapi import Depends,APIRouter
from app.dependecies import sessionDep
from app.manage.autheticaton import sessionDep,Session,oauth2_scheme,get_current_user
from typing import Annotated
from app.models.events_model import Application,Response
from app.models.users_model import User
from fastapi.exceptions import HTTPException
from app.schemas.response_schemas import ResponseCreate,ResponseDisplay,ResponseUpdate


responses_router = APIRouter(prefix='/responses')



@responses_router.post('/add_responses/{app_id}/',deprecated=True)
def add_responses(app_id:int,responses:list[ResponseCreate],token:Annotated[str,Depends(oauth2_scheme)],db:sessionDep):
    application = db.query(Application).filter(Application.id == app_id).first()
    if not application :
        raise HTTPException(404,'this application does not exist')
    user = get_current_user(token,db)
    if not user.user_type == 'PERSON' or user.person.id != application.user_id:
        raise HTTPException('you are not allowed to do this action')
    
    created_ids = []
    for response in responses:
        resp = Response(**response.model_dump())
        db.add(resp)
        db.flush()
        created_ids.append(resp.id)

    db.commit()
    return created_ids
        


def retrieve_response(response_id:int,db:Session):
    return db.query(Response).filter(Response.id == response_id).first()

@responses_router.get('/view_response/{response_id}/', response_model=ResponseDisplay)
def get_response(response_id: int, token: Annotated[str, Depends(oauth2_scheme)], db: sessionDep):
    user = get_current_user(token, db)
    response = retrieve_response(response_id, db)
    if not response:
        raise HTTPException(404, 'Response not found')
    application = db.query(Application).filter(Application.id == response.application_id).first()
    if not application:
        raise HTTPException(404, 'Application not found')
    if not user.user_type == 'PERSON' or user.person.id != application.user_id:
        raise HTTPException(403, 'You are not allowed to view this response')
    return response

@responses_router.put('/update_response/{response_id}/', response_model=ResponseDisplay)
def update_response(response_id: int, response_update: ResponseUpdate, token: Annotated[str, Depends(oauth2_scheme)], db: sessionDep):
    user = get_current_user(token, db)
    response = retrieve_response(response_id, db)
    if not response:
        raise HTTPException(404, 'Response not found')
    application = db.query(Application).filter(Application.id == response.application_id).first()
    if not application:
        raise HTTPException(404, 'Application not found')
    if not user.user_type == 'PERSON' or user.person.id != application.user_id:
        raise HTTPException(403, 'You are not allowed to update this response')
    if response_update.answer is not None:
        response.answer = response_update.answer
    db.commit()
    db.refresh(response)
    return response

@responses_router.get('/application/{app_id}/responses/', response_model=list[ResponseDisplay])
def get_application_responses(app_id: int, token: Annotated[str, Depends(oauth2_scheme)], db: sessionDep):
    user = get_current_user(token, db)
    application = db.query(Application).filter(Application.id == app_id).first()
    if not application:
        raise HTTPException(404, 'Application not found')
    if not user.user_type == 'PERSON' or user.person.id != application.user_id:
        raise HTTPException(403, 'You are not allowed to view these responses')
    responses = db.query(Response).filter(Response.application_id == app_id).all()
    return responses
        
    
    
    
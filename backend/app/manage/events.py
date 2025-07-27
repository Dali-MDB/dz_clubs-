from fastapi import Depends,status
from fastapi.routing import APIRouter
from app.models.events_model import Event,event_status
from app.schemas.event_schemas import EventCreate,EventDisplay,EventUpdate
from app.dependecies import sessionDep,Session
from typing import Annotated
from app.manage.autheticaton import oauth2_scheme,get_current_user
from fastapi.exceptions import HTTPException
from sqlalchemy import desc


event_router = APIRouter(
    prefix='/events'
)


@event_router.post('/add_event/',response_model=EventDisplay)
def add_event(event:EventCreate,token:Annotated[str,Depends(oauth2_scheme)],db:sessionDep):
    user = get_current_user(token,db)
    if user.user_type == 'PERSON':
        raise HTTPException(status.HTTP_403_FORBIDDEN,'only clubs can add events')
    
    event_data = event.model_dump()
    event_data['club_id'] = user.club.id
    event_db = Event(**event_data)
    db.add(event_db)
    db.commit()
    db.refresh(event_db)
    return event_db
    


# a helper function to retrieve an event by id
def retrieve_event(event_id:int,db:Session):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(404,'the event you are looking for does not exist')
    return event


@event_router.get('/get_event/all/',response_model=list[EventDisplay])
def get_all_event(db:sessionDep):
    events = db.query(Event).order_by(desc(Event.date_start)).all()
    return events

@event_router.get('/get_event/{event_id}/',response_model=EventDisplay)
def get_event(event_id:int,db:sessionDep):
    return retrieve_event(event_id,db)


@event_router.put('/update_event/{event_id}/',response_model=EventDisplay)
def update_event(event_id:int,event:EventUpdate,token:Annotated[str,Depends(oauth2_scheme)],db:sessionDep):
    event_db = retrieve_event(event_id,db)
    user = get_current_user(token,db)
    if not user.user_type == 'CLUB' or not user.club.id == event_db.club_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail='you are not allowed to do this action')

    #now we extract new data
    event_data = event.model_dump(exclude_unset=True)
    for key,val in event_data.items():
        setattr(event_db,key,val)

    db.commit()
    db.refresh(event_db)
    return event_db


@event_router.delete('/delete_event/{event_id}')
def delete_event(event_id:int,token:Annotated[str,Depends(oauth2_scheme)],db:sessionDep):
    event_db = retrieve_event(event_id,db)
    user = get_current_user(token,db)
    if not user.user_type == 'CLUB' or not user.club.id == event_db.club_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail='you are not allowed to do this action')
    
    db.delete(event_db)
    db.commit()
    return {'details':'the event has been deleted successfully'}


@event_router.get('/get_club_events/',response_model=dict[event_status,list[EventDisplay]])
def get_all_club_events(club_id:int,db:sessionDep):
    events = db.query(Event).filter(Event.club_id == club_id).order_by(desc(Event.date_start))
    events_dict = {
        event_status.UPCOMING : [],
        event_status.ONGOING : [],
        event_status.OVER : [],
        event_status.CANCELLED : []
    }

    for event in events:
        events_dict[event.status].append(event)

    return events_dict






from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import FileResponse
from app.dependecies import sessionDep
from app.models.users_model import user_types, User
from app.manage.autheticaton import get_current_user, oauth2_scheme
from typing import Annotated
import os
import uuid
from app.models.events_model import Event
from app.schemas.event_schemas import EventDisplay

images_router = APIRouter(prefix='/images')

@images_router.post('/add_profile_image/', response_model=None)
async def add_profile_image(
    db: sessionDep,
    token: Annotated[str, Depends(oauth2_scheme)],
    image: UploadFile = File(...)
):
    user = get_current_user(token, db)
    if user.user_type == user_types.PERSON:
        person = user.person
        # Validate image
        if not image.filename.endswith((".png", ".jpg", ".jpeg")):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='invalid image format')
        # Remove old image if exists
        if person.image_url:
            try:
                os.remove(f'uploaded_files/users/{person.image_url}')
            except FileNotFoundError:
                pass
        # Generate unique name
        person.image_url = f'{person.full_name}_{uuid.uuid4()}.{image.filename.split(".")[-1]}'
        # Save image
        os.makedirs('uploaded_files/users', exist_ok=True)
        with open(f'uploaded_files/users/{person.image_url}', 'wb') as f:
            f.write(await image.read())
        db.commit()
        db.refresh(person)
        return {'message':'image added successfully'}
    else:
        club = user.club
        if not image.filename.endswith((".png", ".jpg", ".jpeg")):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='invalid image format')
        if club.image_url:
            try:
                os.remove(f'uploaded_files/clubs/{club.image_url}')
            except FileNotFoundError:
                pass
        club.image_url = f'{club.name}_{uuid.uuid4()}.{image.filename.split(".")[-1]}'
        os.makedirs('uploaded_files/clubs', exist_ok=True)
        with open(f'uploaded_files/clubs/{club.image_url}', 'wb') as f:
            f.write(await image.read())
        db.commit()
        db.refresh(club)
        return {'message':'image added successfully'}
   

@images_router.get('/get_profile_image/')
def get_profile_image(db: sessionDep, token: Annotated[str, Depends(oauth2_scheme)]):
    user = get_current_user(token, db)
    if user.user_type == user_types.PERSON:
        person = user.person
        if not person.image_url:
            raise HTTPException(status_code=404, detail='No image found for this person')
        return FileResponse(f'uploaded_files/users/{person.image_url}')
    else:
        club = user.club
        if not club.image_url:
            raise HTTPException(status_code=404, detail='No image found for this club')
        return FileResponse(f'uploaded_files/clubs/{club.image_url}')
    

@images_router.get('/get_user_image/{user_id}/')
def get_user_image(user_id:int,db:sessionDep):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail='No user found')
    if user.user_type == user_types.PERSON:
        if user.person.image_url:
            return FileResponse(f'uploaded_files/users/{user.person.image_url}')
        else:
            raise HTTPException(status_code=404, detail='No image found for this person')
    else:
        if user.club.image_url:
            return FileResponse(f'uploaded_files/clubs/{user.club.image_url}')
        else:
            raise HTTPException(status_code=404, detail='No image found for this club')
    


@images_router.delete('/delete_profile_image/')
def delete_profile_image(db: sessionDep, token: Annotated[str, Depends(oauth2_scheme)]):
    user = get_current_user(token, db)
    if user.user_type == user_types.PERSON:
        person = user.person
        if person.image_url:
            try:
                os.remove(f'uploaded_files/users/{person.image_url}')
            except FileNotFoundError:
                pass
            person.image_url = None
            db.commit()
            db.refresh(person)
        return {'message':'image deleted successfully'}
    else:
        club = user.club
        if club.image_url:
            try:
                os.remove(f'uploaded_files/clubs/{club.image_url}')
            except FileNotFoundError:
                pass
            club.image_url = None
            db.commit()
            db.refresh(club)
        return {'message':'image deleted successfully'}







#attach image to an event (only club )
@images_router.post('/attach_image_to_event/{event_id}/',response_model=EventDisplay)
async def attach_image_to_event(event_id:int,db:sessionDep,token:Annotated[str,Depends(oauth2_scheme)],image:UploadFile=File(...)):
    user = get_current_user(token,db)
    if user.user_type != user_types.CLUB:
        raise HTTPException(status_code=403, detail='You are not allowed to attach an image to an event')
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail='No event found')
    if event.club_id != user.club.id:
        raise HTTPException(status_code=403, detail='You are not allowed to attach an image to this event')
    if not image.filename.endswith((".png", ".jpg", ".jpeg")):
        raise HTTPException(status_code=400, detail='invalid image format')
    os.makedirs('uploaded_files/events',exist_ok=True)
    if event.image_url:
        try:
            os.remove(f'uploaded_files/events/{event.image_url}')
        except FileNotFoundError:
            pass
    event.image_url = f'{event.name}_{uuid.uuid4()}.{image.filename.split(".")[-1]}'
    with open(f'uploaded_files/events/{event.image_url}','wb') as f:
        f.write(await image.read())
    db.commit()
    db.refresh(event)
    return event


#delete image from an event (only club)
@images_router.delete('/delete_image_from_event/{event_id}/')
def delete_image_from_event(event_id:int,db:sessionDep,token:Annotated[str,Depends(oauth2_scheme)]):
    user = get_current_user(token,db)
    if user.user_type != user_types.CLUB:
        raise HTTPException(status_code=403, detail='You are not allowed to delete an image from an event')
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail='No event found')
    if event.club_id != user.club_id:
        raise HTTPException(status_code=403, detail='You are not allowed to delete an image from this event')
    
    if event.image_url:
        os.remove(f'uploaded_files/events/{event.image_url}')
        event.image_url = None
    db.commit()
    db.refresh(event)
    return {'message':'image deleted successfully'}


#get image from an event 
@images_router.get('/get_event_image/{event_id}/')
def get_event_image(event_id:int,db:sessionDep):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail='No event found')
    if event.image_url:
        return FileResponse(f'uploaded_files/events/{event.image_url}')
    else:
        raise HTTPException(status_code=404, detail='No image found for this event')

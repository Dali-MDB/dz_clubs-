from fastapi import Depends,APIRouter,status,Body
from app.dependecies import sessionDep,Session
from app.models.users_model import Club
from app.models.events_model import Event
from fastapi import HTTPException
from app.schemas.club_schemas import ClubDisplay,ClubUpdate
from app.manage.autheticaton import get_current_user,oauth2_scheme
from typing import Annotated
from sqlalchemy import desc
from app.schemas.event_schemas import EventDisplay
import os
from dotenv import load_dotenv

load_dotenv()  # loads from .env in root dir
app_key = os.getenv("APP_KEY")

club_router = APIRouter(
    prefix='/clubs'
)




def retrieve_club(club_id:int,db:Session):
    club = db.query(Club).filter(Club.id == club_id).first()
    if not club:
        raise HTTPException(status_code=404,detail='Club not found')
    return club



@club_router.get('/view_club/{club_id}/',response_model=ClubDisplay)
def view_club(club_id:int,db:sessionDep):
    club = retrieve_club(club_id,db)
    return club


@club_router.get('/view_all_clubs/',response_model=list[ClubDisplay])
def view_all_clubs(db:sessionDep):
    clubs = db.query(Club).all()
    return clubs


@club_router.put('/edit_club/{club_id}/',response_model=ClubDisplay)
def edit_club(club_id:int,club:ClubUpdate,token:Annotated[str,Depends(oauth2_scheme)],db:sessionDep):
    club_db = retrieve_club(club_id,db)
    #verify permissions
    user = get_current_user(token,db)
    if user.user_type == 'PERSON' or user.club.id != club_db.id:
        raise HTTPException(status_code=403,detail='You are not allowed to edit this club')
    
    club_data = club.model_dump(exclude_unset=True)
    for field,value in club_data.items():
        setattr(club_db,field,value)
    db.commit()
    db.refresh(club_db)
    return club_db




@club_router.delete('/delete_club/{club_id}/')
def delete_club(club_id:int,token:Annotated[str,Depends(oauth2_scheme)],db:sessionDep):
    club_db = retrieve_club(club_id,db)
    user = get_current_user(token,db)
    if user.user_type == 'PERSON' or user.club.id != club_db.id:
        raise HTTPException(status_code=403,detail='You are not allowed to delete this club')
    #delete all events associated with the club
    db.query(Event).filter(Event.club_id == club_id).delete()
    #delete the club
    db.delete(club_db)
    db.commit()
    return {'details':'Club deleted successfully'}



@club_router.get('/get_club_events/self/',response_model=list[EventDisplay])
def get_club_events(token:Annotated[str,Depends(oauth2_scheme)],db:sessionDep):
    user = get_current_user(token,db)
    if user.user_type == 'PERSON':
        raise HTTPException(status_code=403,detail='You are not allowed to get club events')
    events = db.query(Event).filter(Event.club_id == user.club.id).order_by(desc(Event.date_start))
    return events











@club_router.get('/get_mail_credential_app-key/')
def get_mail_credential_app(token:Annotated[str,Depends(oauth2_scheme)],db:sessionDep):
    user = get_current_user(token,db)
    frnt = Fernet(app_key) 
    if user.user_type != 'CLUB':
        raise HTTPException(403,'only clubs are allowed to do this action')
    return {
        'api_key' : frnt.decrypt(user.club.code_mail).decode(),
        'exist' : True if user.club.code_mail else False
    }




import smtplib
from cryptography.fernet import Fernet
@club_router.post('/add_mail_credential_app-key/')
def add_mail_credential_app(key:Annotated[str,Body()],token:Annotated[str,Depends(oauth2_scheme)],db:sessionDep):
    user = get_current_user(token,db)
    if user.user_type != 'CLUB':
        raise HTTPException(403,'only clubs are allowed to do this action')

    frnt = Fernet(app_key)
    encrypted_code =  frnt.encrypt(key.encode())
    #we try to login the user to confirm compatibiliy
    try:
        with smtplib.SMTP("smtp.gmail.com",587) as server:
            server.starttls()
            server.login(user.email,key)
    except: #unvalid credentials
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail='the api key that you provided is unvalid,try regenerating another one')
    user.club.code_mail = encrypted_code
    db.commit()
    return {'detail':'api key for email was added successfully'}


@club_router.get('/test_key/')
async def test_key(key:str):
    frnt = Fernet(app_key)
    print("here1\n\n\n\n")
    encrypted =  frnt.encrypt(key.encode())
    print("here2\n\n\n\n")
    decrypted = frnt.decrypt(encrypted).decode()
    print("here3\n\n\n\n")
    return {
        'key' : app_key,
        'encrypted' : encrypted,
        'decrypted' : decrypted
    }
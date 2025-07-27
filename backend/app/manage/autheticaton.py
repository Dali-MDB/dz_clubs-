from jose import jwt
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from passlib.context import CryptContext
from datetime import datetime,timedelta
from app.schemas.user_schemas import UserCreate,UserDisplay
from app.schemas.person_schemas import PersonCreate,PersonDisplay
from app.schemas.club_schemas import ClubCreate,ClubDisplay
from app.dependecies import sessionDep
from app.models.users_model import User,Person,Club
from fastapi.exceptions import HTTPException
from fastapi import status
from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import Depends

from fastapi.routing import APIRouter




SECRET_KEY = 'zHtN3UQZV+BtqS8XsVvGNf2T9OfP?0542-+=84N6jrJVmGlvDFa8gd5XpVqzT1RYD6g7M'
ALGORITH = 'HS256'
ACCESS_TOKEN_EXPIRES_MINUTES = 120


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth/login/')

pwd_context = CryptContext(schemes=['bcrypt'],deprecated='auto')




def create_token(data:dict):
    to_encode = data.copy()
    expirey_time = datetime.now() + timedelta(ACCESS_TOKEN_EXPIRES_MINUTES)
    to_encode['exp'] = expirey_time
    return jwt.encode(to_encode,SECRET_KEY,ALGORITH)




auth_router = APIRouter(
    prefix='/auth'
)



#a utility function to create the user instance in db
def register_user(user:UserCreate,db:Session):
    #first we check if this user already exists
    user_indb = db.query(User).filter(User.email == user.email).first()
    if user_indb:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="user with this username/email is already registered")
    user_data = user.model_dump()
    hashed_password = pwd_context.hash(user.password)
    user_data['password'] = hashed_password
    return User(**user_data)




@auth_router.post('/register/person/',response_model=PersonDisplay)
async def register_person(user:UserCreate,person:PersonCreate,db:sessionDep):
    #create the user
    user_db = register_user(user,db)
    db.add(user_db)
    db.commit()
    db.refresh(user_db)
    #create the person
    person_data = person.model_dump()
    person_data.update({'user_id':user_db.id})
   
    person_db = Person(**person_data)

    db.add(person_db)
    db.commit()
    db.refresh(person_db)
    return person_db


@auth_router.post('/register/club/',response_model=ClubDisplay)
async def register_club(user:UserCreate,club:ClubCreate,db:sessionDep):
    #create the user
    user_db = register_user(user,db)
    user_db.user_type = 'CLUB'
    db.add(user_db)
    db.commit()
    db.refresh(user_db)
    #create the person
    club_data = club.model_dump()
    club_data.update({'user_id':user_db.id})
   
    club_db = Club(**club_data)

    db.add(club_db)
    db.commit()
    db.refresh(club_db)
    return club_db
    
    



#a helper function to authenticate
def authenticate(email:str,password:str,db:Session):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return False
    #we validate credentials
    if not pwd_context.verify(password,user.password):
        return False
    return user    #authenticated successfully



@auth_router.post('/login/')
def login(form_data : Annotated[OAuth2PasswordRequestForm,Depends()],db:sessionDep):
    email = form_data.username
    password = form_data.password
    user = authenticate(email,password,db)
    if not user:
        raise HTTPException(
            status_code=401,
            detail='we could not authenticate you, verify your username or password'
        )
    
    #we generate an access token for our user
    data = {
        'sub' : user.email,
        'user_id' : user.id
    }

    token = create_token(data)
    return {
        "access_token" : token,
        "token_type" : "bearer"
    }




@auth_router.get('/test/')
def secured_endpoint(token:Annotated[str,Depends(oauth2_scheme)]):
    return {'derails':'you can view this page'}





def get_current_user(token:str,db:Session):
    payload = jwt.decode(token,SECRET_KEY,ALGORITH)

    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    email = payload['sub']

    user = db.query(User).filter(User.email==email).first()
    return user
    

@auth_router.get('/current_user/',response_model=UserDisplay)
def current_user(token:Annotated[str,Depends(oauth2_scheme)],db:sessionDep):
    return  get_current_user(token,db)


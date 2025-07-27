from typing import Annotated, List
from fastapi import Depends,APIRouter, HTTPException
from pydantic import EmailStr
from app.dependecies import sessionDep
from app.manage.clubs import retrieve_club
from app.models.users_model import User
from app.schemas.person_schemas import PersonDisplay
from app.manage.autheticaton import get_current_user, oauth2_scheme
from fastapi import UploadFile
from fastapi import status


membership_router = APIRouter(prefix='/membership')



@membership_router.get('/get_all_members/{club_id}/',response_model=List[PersonDisplay])
def get_all_members(club_id:int,db:sessionDep):
    club = retrieve_club(club_id,db)
    return club.members



@membership_router.get('/get_all_members/self/',response_model=List[PersonDisplay])
def get_all_members_self(club_id:int,token:Annotated[str,Depends(oauth2_scheme)],db:sessionDep):
    user = get_current_user(token,db)
    if not user.user_type == 'CLUB':
        raise HTTPException(403,'you are not allowed to vieww this page as a user')
    
    return user.club.members


@membership_router.post('/add_member/')
def add_member(email:EmailStr,token:Annotated[str,Depends(oauth2_scheme)],db:sessionDep):
    user = get_current_user(token,db)
    if not user.user_type == 'CLUB':
        raise HTTPException(403,'you are not allowed to vieww this page as a user')
    
    new_member = db.query(User).filter(User.email == email).first()
    if not new_member:
        raise HTTPException(404,'this user does not exist')
    club = user.club
    #check if the member is already a member of the club
    if new_member.person in club.members:
        raise HTTPException(400,'this user is already a member of the club')
    
    club.members.append(new_member.person)
    db.commit()
    return {'message':'member added successfully',
            'member_id':new_member.person.id}



@membership_router.delete('/remove_member/')
def remove_member(email:EmailStr,token:Annotated[str,Depends(oauth2_scheme)],db:sessionDep):
    user = get_current_user(token,db)
    if not user.user_type == 'CLUB':
        raise HTTPException(403,'you are not allowed to vieww this page as a user')
    
    club = user.club
    member = db.query(User).filter(User.email == email).first()
    if not member:
        raise HTTPException(404,'this user does not exist')
    
    if member.person not in club.members:
        raise HTTPException(400,'this user is not a member of the club')
    
    club.members.remove(member.person)
    db.commit()
    return {'message':'member removed successfully',
            'member_id':member.person.id}





import pandas as pd
import io
import zipfile
from fastapi.responses import StreamingResponse,Response
@membership_router.post(('/upload_members_file/'))
async def upload_members_file(token:Annotated[str,Depends(oauth2_scheme)],file:UploadFile,db:sessionDep):
    #verify user
    
    user = get_current_user(token,db)
    if user.user_type != 'CLUB':
        raise HTTPException(403,'only clubs are allowed to do this action')
    
    #verify it is a valid csv 
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail='only csv files are accepted')
    
    members = pd.read_csv(file.file)
    #verify columns
    members.columns = members.columns.str.lower()
    if  'email' not in members.columns:
        raise HTTPException(400,'the file you uploaded must have an email column for members')
    emails = list(members['email'])

    users_in_db = db.query(User).filter(User.email.in_(emails) ).all()
    emails_in_db =[x.email for x in users_in_db]


    non_existent = []
    already_members = []
    added_members = []
    club = user.club
    print(club.members)
    for email in emails:
        if email not in emails_in_db:
            non_existent.append(email)
        else:
            user_db = users_in_db[emails_in_db.index(email)] 
            #check if the user is already a member
            if user_db.user_type == 'CLUB':    #error , trying to add a club
                continue
        
            if user_db.person in club.members:
                already_members.append(email)
            else:
                club.members.append(user_db.person)
                added_members.append(email)
        
    #we return info 
    db.commit()
    non_ex_df = pd.DataFrame(non_existent,columns=['email'])
    alr_mmb_df = pd.DataFrame(already_members,columns=['email'])
    add_mmb_df = pd.DataFrame(added_members,columns=['email'])



    #compress the three dfs into one zip file to return
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer,'a',zipfile.ZIP_DEFLATED,False) as zip_file:
        zip_file.writestr("nonexistent_emails.csv", non_ex_df.to_csv(index=False))
        zip_file.writestr("existing_members.csv", alr_mmb_df.to_csv(index=False))
        zip_file.writestr("added_members.csv", add_mmb_df.to_csv(index=False))


    zip_buffer.seek(0)   #return to start
    return StreamingResponse(
        content=zip_buffer,
        media_type="application/zip",
        headers={
            "Content-Disposition": "attachment; filename=all_reports.zip",
            "Access-Control-Expose-Headers": "Content-Disposition"
        }
    )

   

from fastapi import APIRouter,status,UploadFile
from app.manage.autheticaton import get_current_user,oauth2_scheme
from app.dependecies import sessionDep
from app.manage.events import retrieve_event
from fastapi import Depends,HTTPException
from typing import Annotated
from app.models.events_model import Application,application_status,Response
from app.schemas.application_schemas import ApplicationCreate,ApplicationDisplay
from datetime import datetime
from app.schemas.response_schemas import ResponseCreate




application_router = APIRouter(
    prefix='/applications'
)


@application_router.post('/apply_for_event/{event_id}/',response_model=ApplicationDisplay)
def apply_for_event(event_id:int,application : ApplicationCreate,responses:list[ResponseCreate],token:Annotated[str,Depends(oauth2_scheme)],db:sessionDep):
    user = get_current_user(token,db)
    if user.user_type == 'CLUB':
        raise HTTPException(status_code=403,detail='You are not allowed to apply for this event as a club')
    #we check if the user has already applied for this event
    application_db = db.query(Application).filter(Application.user_id == user.person.id,Application.event_id == event_id).first()
    if application_db:
        raise HTTPException(status_code=400,detail='You have already applied for this event')
    #we create the application
    application_data = application.model_dump()
    application_data.update(
        {
            'user_id' : user.person.id,
            'submitted_at' : datetime.now(),
            'event_id' : event_id,
            'status' : 'PENDING',
            'email' : user.email,
            'phone' : user.person.phone,
        }
    )
    application_db = Application(**application_data)
    db.add(application_db)
    db.flush()
    for response in responses:
        response_data = response.model_dump()
        response_data['application_id'] = application_db.id
        resp = Response(**response_data)
        db.add(resp)

    db.commit()
    db.refresh(application_db)
    return application_db



@application_router.delete('/cancel_application/{app_id}')
def cancel_application(app_id:int,token:Annotated[str,Depends(oauth2_scheme)],db:sessionDep):
    user = get_current_user(token,db)
    if user.user_type == 'CLUB':
        raise HTTPException(status.HTTP_400_BAD_REQUEST,'you can not perform this action as a club')
    application = db.query(Application).filter(Application.id == app_id,Application.user_id==user.person.id).first()
    if not application:
        raise HTTPException(404,'no application was found')
    if application.status != 'PENDING':
        raise HTTPException(400,'you can only cancel pending applicarions')
    application.status = application_status.CANCELLED
    db.commit()
    return {'details':'the application has been cancelled successfully'}
    



@application_router.get('/view_my_applications/',response_model=dict[application_status,list[ApplicationDisplay]])
def view_my_applications(token:Annotated[str,Depends(oauth2_scheme)],db:sessionDep):
    user = get_current_user(token,db)
    if user.user_type =='CLUB':
        raise HTTPException('clubs can not have applications')
    
    apps = {
        application_status.PENDING : [],
        application_status.ACCEPTED : [],
        application_status.REJECTED : [],
    }

    applications = db.query(Application).filter(Application.user_id == user.person.id).all()
    print("here",len(applications))
    for app in applications:
        print(app.motivation)
        apps[app.status].append(app)

    return apps





@application_router.post('/accept_application/{app_id}/')
def accept_application(app_id: int, token: Annotated[str, Depends(oauth2_scheme)], db: sessionDep):
    user = get_current_user(token, db)
    if user.user_type != 'CLUB':
        raise HTTPException(status_code=403, detail='Only clubs can accept applications')
    application = db.query(Application).filter(Application.id == app_id).first()
    if not application:
        raise HTTPException(status_code=404, detail='Application not found')
    event = application.event
    if not event or event.club_id != user.club.id:
        raise HTTPException(status_code=403, detail='You are not allowed to accept applications for this event')
    if application.status != application_status.PENDING:
        raise HTTPException(status_code=400, detail='Only pending applications can be accepted')
    application.status = application_status.ACCEPTED
    db.commit()
    db.refresh(application)
    return {'details': 'Application accepted successfully', 'application_id': application.id}


@application_router.post('/reject_application/{app_id}/')
def reject_application(app_id: int, token: Annotated[str, Depends(oauth2_scheme)], db: sessionDep):
    user = get_current_user(token, db)
    if user.user_type != 'CLUB':
        raise HTTPException(status_code=403, detail='Only clubs can reject applications')
    application = db.query(Application).filter(Application.id == app_id).first()
    if not application:
        raise HTTPException(status_code=404, detail='Application not found')
    event = application.event
    if not event or event.club_id != user.club.id:
        raise HTTPException(status_code=403, detail='You are not allowed to reject applications for this event')
    if application.status != application_status.PENDING:
        raise HTTPException(status_code=400, detail='Only pending applications can be rejected')
    application.status = application_status.REJECTED
    db.commit()
    db.refresh(application)
    return {'details': 'Application rejected successfully', 'application_id': application.id}



@application_router.get('/get_event_applications/{event_id}/',response_model=list[ApplicationDisplay])
def get_event_applications(event_id:int,token:Annotated[str,Depends(oauth2_scheme)],db:sessionDep):
    event = retrieve_event(event_id,db)
    user = get_current_user(token,db)
    #check for user permissions
    if user.user_type == 'PERSON' or user.club.id != event.club_id:
        raise HTTPException(403,'you are not allowed to do this action since you are not the owner of this event')
    return event.applications




from app.manage.cleaning_tasks import create_applications
from fastapi import BackgroundTasks
from app.models.users_model import User
import pandas as pd
@application_router.post('/synchronize_application/{event_id}/')
def synchronize_application(event_id:int,token:Annotated[str,Depends(oauth2_scheme)],db:sessionDep,sheet:UploadFile,background_tasks: BackgroundTasks):
    event = retrieve_event(event_id,db)
    
    user = get_current_user(token,db)
    #check for user permissions
    if user.user_type == 'PERSON' or user.club.id != event.club_id:
        raise HTTPException(403,'you are not allowed to do this action since you are not the owner of this event')
    
    #check file extension
    if not sheet.filename.endswith('.csv'):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail='only csv files are accepted')
    
    apps = event.applications
    applicants_mails = set(x.email for x in apps)
    print(applicants_mails)

    df_mails = pd.read_csv(sheet.file)
    new_applicants = []
    for index,row in df_mails.iterrows():
        mail = row['email']
        if mail not in applicants_mails:
            #we create an application with this mail
            new_app = Application(
                email = mail,
                motivation = str(row.drop(labels='email').to_dict()),
                submitted_at = datetime.now(),
                from_app = False,     #cuz added from extra parties not through app application
                event_id = event_id
            )
            print(new_app.motivation)
            db.add(new_app)
            new_applicants.append(mail)
            applicants_mails.add(mail)   #carch duplicates
    db.commit()


    #vice versa operation
    df_mails = set(df_mails['email'])
    notify_sheet = []
    for mail in applicants_mails:
        if mail not in df_mails:
            notify_sheet.append(mail)

    background_tasks.add_task(create_applications,event_id,new_applicants,db)
    return {
        'details' : 'the new applications have been added successfully',
        'in_app_not_in_sheet' : notify_sheet,
    }
    



from pydantic import BaseModel
class MailContent(BaseModel):
    subject:str
    content:str


from app.manage.email import send_email
@application_router.post('/send_mails/{event_id}/',status_code=status.HTTP_200_OK)
def send_mails(event_id:int,mail_content_accepted:MailContent,mail_content_rejected:MailContent,token:Annotated[str,Depends(oauth2_scheme)],db:sessionDep,background_tasks:BackgroundTasks):
    event = retrieve_event(event_id,db)
    user = get_current_user(token,db)
    if user.user_type == 'PERSON' or user.club.id != event.club_id:
        raise HTTPException(403,'you are not allowed to do this action since you are not the owner of this event')
    
    #get all the applications
    apps = event.applications
    #split them into accepted and rejected
    accepted_apps = [app.email for app in apps if app.status == application_status.ACCEPTED]
    rejected_apps = [app.email for app in apps if app.status == application_status.REJECTED]
    

    send_email()
    background_tasks.add_task(send_email,user.email,user.club.code_mail,mail_content_accepted.subject,mail_content_accepted.content,accepted_apps)
    background_tasks.add_task(send_email,user.email,user.club.code_mail,mail_content_rejected.subject,mail_content_rejected.content,rejected_apps)
    background_tasks.add_task()


    return {'details':'mails have been sent successfully'}
    
    
    
from fastapi import APIRouter,BackgroundTasks
from app.manage.cleaning_tasks import update_events_status
from app.dependecies import sessionDep
from app.manage.email import send_email

utils_api = APIRouter(prefix='/utils')


@utils_api.get('/bg/')
def bg(db:sessionDep,background_tasks: BackgroundTasks):
    background_tasks.add_task(update_events_status,db)
    return {'gg':'gg'}



@utils_api.get('/mail/')
def mail():
   send_email('test','this is a test message')
   return {'gg':'gg'}


from app.manage.cleaning_tasks import delete_responses
@utils_api.get('/del_resp/')
def del_resp(event_id:int,db:sessionDep):
    delete_responses(event_id,db)
    

from cryptography.fernet import Fernet
@utils_api.get('/get_key/')
def get_key():
    return Fernet.generate_key()
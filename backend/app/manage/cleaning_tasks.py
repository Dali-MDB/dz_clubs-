from app.models.events_model import Event,event_status,Application,Response
from app.models.users_model import User,user_types
from app.dependecies import Session
from datetime import datetime
import os



def update_events_status(db:Session):
    now = datetime.now()
    file_name = 'app/manage/last_events.txt'
    with open(file_name, 'r+') as f:
        line = f.readline().strip()   
        if line: 
            last_time = datetime.strptime(line, "%Y-%m-%d %H:%M:%S")
        else:   #the file was empty
            f.seek(0)    
            f.write(now.strftime("%Y-%m-%d %H:%M:%S"))   #we fill with current time
            last_time = now
        delta = now - last_time
        hours_diff = delta.total_seconds() / 3600

        if hours_diff < 6:
            return
    
    

    #upcoming
    db.query(Event).filter(
        Event.date_start > now ,
        Event.status != event_status.CANCELLED
        ).update(
            {
            "status" : event_status.UPCOMING,
            }
        )
    
    #ongoing
    db.query(Event).filter(
        Event.date_start <= now ,
        Event.date_end > now,
        Event.status != event_status.CANCELLED
        ).update(
            {
            "status" : event_status.ONGOING,
            }
        )
    
    #over
    db.query(Event).filter(
        Event.date_end < now,
        Event.status != event_status.CANCELLED
        ).update(
            {
            "status" : event_status.OVER,
            }
        )
    
    db.commit()
    with open(file_name, 'r+') as f:
        f.write(now.strftime("%Y-%m-%d %H:%M:%S"))

    



def create_applications(event_id:int,mails:list[str],db:Session):
    users = db.query(User).filter(User.email.in_(mails))
    users_mails = [user.email for user in users]
    applications = db.query(Application).filter(Application.event_id == event_id,Application.email.in_(users_mails))
    for app in applications:
        user = users[users_mails.index(app.email)]
        if user.user_type == user_types.PERSON: 
            app.user_id = user.person.id

    db.commit()
    print('gg ma nega')




from sqlalchemy import select
def delete_responses(event_id:int,db:Session):
    app_ids = select(Application.id).where(Application.event_id == event_id)
    db.query(Response).filter(Response.application_id.in_(app_ids)).delete(synchronize_session=False)
    db.commit()


from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.manage.membership import membership_router
from app.manage.autheticaton import auth_router
from app.manage.events import event_router
from app.manage.clubs import club_router
from app.manage.applications import application_router
from app.manage.questions import question_router
from app.manage.responses import responses_router
from app.manage.users import user_router
from app.manage.images import images_router
from app.manage.utils import utils_api

from fastapi.middleware.cors import CORSMiddleware






app = FastAPI()
#add cors
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   #for now
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/uploads", StaticFiles(directory="uploaded_files"), name="uploads")

app.include_router(auth_router,tags=['authentication'])
app.include_router(event_router,tags=['events'])
app.include_router(club_router,tags=['clubs'])
app.include_router(application_router,tags=['applications'])
app.include_router(question_router,tags=['questions'])
app.include_router(responses_router,tags=['responses'])
app.include_router(user_router,tags=['users'])
app.include_router(membership_router,tags=['membership'])
app.include_router(images_router,tags=['images'])
app.include_router(utils_api,tags=['utils'])


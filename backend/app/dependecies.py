from fastapi import Depends
from sqlalchemy.orm import Session
from app.database import session_local
from typing import Annotated





def get_db():
    db = session_local()
    try:
        yield db
    finally:
        db.close()


sessionDep = Annotated[Session, Depends(get_db)]
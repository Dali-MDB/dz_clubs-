from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQL_DB_URL = 'sqlite:///./clubs_db.db'
engine = create_engine(SQL_DB_URL,connect_args={"check_same_thread": False})

session_local = sessionmaker(bind=engine,autoflush=False,autocommit=False)

Base = declarative_base()
from app.database import Base
from sqlalchemy import Column,String,Text,Integer,DateTime,Enum,ForeignKey
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum



class event_types(str,PyEnum):
    INTERNAL = 'INTERNAL'
    EXTERNAL = 'EXTERNAL'

class event_status(str,PyEnum):
    UPCOMING = 'UPCOMING'
    ONGOING = 'ONGOING'
    OVER = 'OVER'
    CANCELLED = 'CANCELLED'

class Event(Base):
    __tablename__ = 'Events'

    id = Column(Integer,unique=True,primary_key=True)
    name = Column(String(30))
    date_start = Column(DateTime,index=True)
    date_end = Column(DateTime)
    venue = Column(String(50))
    description = Column(Text,nullable=True)
    event_type = Column(Enum(event_types))
    content = Column(String(30),index=True)
    status = Column(Enum(event_status),default=event_status.UPCOMING)

    club_id = Column(Integer,ForeignKey('Clubs.id'))


    club = relationship('Club',back_populates='events')
    applications = relationship('Application',back_populates='event')



class application_status(str,PyEnum):
    PENDING = 'PENDING'
    ACCEPTED = 'ACCEPTED'
    REJECTED = 'REJECTED'

class Application(Base):
    __tablename__ = 'Applications'

    id = Column(Integer,unique=True,primary_key=True)
    user_id = Column(Integer,ForeignKey('Persons.id'))
    motivation = Column(Text)
    submitted_at = Column(DateTime)
    event_id = Column(Integer,ForeignKey('Events.id'))
    status = Column(Enum(application_status))

    person = relationship('Person',back_populates='applications')
    event = relationship(Event,back_populates='applications')

from app.database import Base
from sqlalchemy import Column,String,Text,Integer,DateTime,Enum,ForeignKey,URL,Boolean
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
    sheet = Column(String(255),nullable=True)
    image_url = Column(String(255),nullable=True)

    club_id = Column(Integer,ForeignKey('Clubs.id'))


    club = relationship('Club',back_populates='events')
    applications = relationship('Application',back_populates='event')
    questions = relationship('Question',back_populates='event')


    @property
    def club_name(self):
        return self.club.name




class question_types(str, PyEnum):
    TEXT = "text"
    RADIO = "radio"
    CHECKBOX = "checkbox"
    DROPDOWN = "dropdown"


class Question(Base):
    __tablename__ = "Questions"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("Events.id"))
    text = Column(String(500)) 
    question_type = Column(Enum(question_types))  
    options = Column(Text, nullable=True)  # Comma-separated
    is_required = Column(Boolean, default=True)

    event = relationship("Event", back_populates="questions")
    responses = relationship('Response',back_populates='question')



class application_status(str,PyEnum):
    PENDING = 'PENDING'
    ACCEPTED = 'ACCEPTED'
    REJECTED = 'REJECTED'
    CANCELLED = 'CANCELLED'

class Application(Base):
    __tablename__ = 'Applications'

    id = Column(Integer,unique=True,primary_key=True)
    user_id = Column(Integer,ForeignKey('Persons.id'),nullable=True)
    email = Column(String)
    motivation = Column(Text)
    submitted_at = Column(DateTime)
    from_app = Column(Boolean,default=True)
    event_id = Column(Integer,ForeignKey('Events.id'))
    status = Column(Enum(application_status),default=application_status.PENDING)

    person = relationship('Person',back_populates='applications')
    event = relationship(Event,back_populates='applications')
    responses = relationship('Response',back_populates='application')



   




class Response(Base):
    __tablename__ = "Responses"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("Applications.id"))
    question_id = Column(Integer, ForeignKey("Questions.id"))
    answer = Column(Text)  
    question = relationship("Question",back_populates='responses')  
    application = relationship("Application", back_populates="responses")


    @property
    def question_text(self):
        return self.question.text
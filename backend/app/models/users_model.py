from app.database import Base
from sqlalchemy.orm import relationship
from sqlalchemy import Table,Column,Integer,String,Text,Date,Enum,CheckConstraint,ForeignKey
from enum import Enum as PyEnum

class user_types(str,PyEnum):
    PERSON = "PERSON"
    CLUB = "CLUB"



class User(Base):
    __tablename__ = 'Users'

    id = Column(Integer,unique=True,primary_key=True)
    email = Column(String(50),unique=True,index=True)
    password = Column(Text)
    user_type = Column(Enum(user_types),default=user_types.CLUB)

    person = relationship('Person',back_populates='user',uselist=False)
    club = relationship('Club',back_populates='user',uselist=False)


class Person(Base):
    __tablename__ = 'Persons'

    id = Column(Integer,unique=True,primary_key=True)
    user_id = Column(Integer,ForeignKey('Users.id'),unique=True)

    full_name = Column(String(50))
    university = Column(String(50),index=True)
    phone = Column(String(20), nullable=True)
    major = Column(String(50),index=True)
    year = Column(Integer)
    city = Column(String(20),nullable=True,index=True)


    user = relationship(User,back_populates='person')
    clubs = relationship('Club',secondary='Membership',back_populates='members')
    applications = relationship('Application',back_populates='person')

    __table_args__ = (
        CheckConstraint("year >= 1 AND year <= 5",name="year constraint"),
    )



class Club(Base):
    __tablename__ = 'Clubs'

    id = Column(Integer,primary_key=True,unique=True)
    user_id = Column(Integer,ForeignKey('Users.id'),unique=True)

    name = Column(String(50),index=True)
    university = Column(String(50),index=True)
    address = Column(String(100),nullable=True)
    description = Column(Text,nullable=True)
    phone = Column(String(20),nullable=True)

    user = relationship(User,back_populates='club')
    members = relationship(Person,secondary='Membership',back_populates='clubs')
    events = relationship('Event',back_populates='club')


Membership = Table(
    'Memberships',
    Base.metadata,
    Column('person_id',Integer,ForeignKey('Persons.id'),primary_key=True),
    Column('club_id',Integer,ForeignKey('Clubs.id'),primary_key=True),
)
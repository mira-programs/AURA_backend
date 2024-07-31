from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from database import Base

# Association table for the many-to-many relationship
completed_challenges = Table(
    'completed_challenges',
    Base.metadata,
    Column('account_id', Integer, ForeignKey('accounts.id'), primary_key=True),
    Column('challenge_id', Integer, ForeignKey('challenges.id'), primary_key=True)
)

# Association table for the many-to-many relationship between friends
friends = Table(
    'friends',
    Base.metadata,
    Column('account_id', Integer, ForeignKey('accounts.id'), primary_key=True),
    Column('friend_id', Integer, ForeignKey('accounts.id'), primary_key=True)
)

class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    points = Column(Integer, default=0)
    first_name = Column(String, nullable=True)   
    last_name = Column(String, nullable=True)

    completed_challenges = relationship(
        'Challenge',
        secondary=completed_challenges,
        back_populates='completed_by'
    )
    
    friends = relationship(
        'Account',
        secondary=friends,
        primaryjoin=id == friends.c.account_id,
        secondaryjoin=id == friends.c.friend_id
    )

class Challenge(Base):
    __tablename__ = "challenges"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, unique=True, index=True)
    points = Column(Integer)

    completed_by = relationship(
        'Account',
        secondary=completed_challenges,
        back_populates='completed_challenges'
    )

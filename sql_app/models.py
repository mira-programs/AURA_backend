from sqlalchemy import Column, Integer, String, ForeignKey, Table, Boolean
from sqlalchemy.orm import relationship
from database import Base

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

    accepted_challenges = relationship(
        'ChallengeStatus',
        back_populates='account'
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
        'ChallengeStatus',
        back_populates='challenge'
    )

class ChallengeStatus(Base):
    __tablename__ = "challenge_status"

    account_id = Column(Integer, ForeignKey('accounts.id'), primary_key=True)
    challenge_id = Column(Integer, ForeignKey('challenges.id'), primary_key=True)
    completed = Column(Boolean, default=False)
    failed = Column(Boolean, default=False)

    account = relationship('Account', back_populates='accepted_challenges')
    challenge = relationship('Challenge', back_populates='completed_by')

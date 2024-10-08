from pydantic import BaseModel, Field, EmailStr

class AccountBase(BaseModel):
    email: str
    username: str
    first_name: str = None
    last_name: str = None

class AccountCreate(AccountBase):
    password: str  

class Account(AccountBase):
    id: int
    points: int = 0
    completed_challenges: list['ChallengeStatus'] = []
    friends: list['Account'] = []

    class Config:
        from_attributes = True

class AccountUpdateUsername(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    
class AccountUpdateEmail(BaseModel):
    email: EmailStr

class ChallengeBase(BaseModel):
    description: str
    points: int

class ChallengeCreate(ChallengeBase):
    pass

class Challenge(ChallengeBase):
    id: int
    completed_by: list['ChallengeStatus'] = []

    class Config:
        from_attributes = True

class ChallengeStatus(BaseModel):
    account_id: int
    challenge_id: int
    completed: bool = False
    failed: bool = False

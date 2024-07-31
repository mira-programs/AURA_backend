from pydantic import BaseModel, Field, EmailStr

class AccountBase(BaseModel):
    email: str
    username: str

class AccountCreate(AccountBase):
    password: str

class Account(AccountBase):
    id: int
    completed_challenges: list['Challenge'] = []

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
    completed_by: list[Account] = []

    class Config:
        from_attributes = True

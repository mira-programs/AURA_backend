from pydantic import BaseModel

class AccountBase(BaseModel):
    email: str
    username: str

class AccountCreate(AccountBase):
    password: str

class Account(AccountBase):
    id: int
    completed_challenges: list['Challenge'] = []

    class Config:
        orm_mode = True

class ChallengeBase(BaseModel):
    description: str
    points: int

class ChallengeCreate(ChallengeBase):
    pass

class Challenge(ChallengeBase):
    id: int
    completed_by: list[Account] = []

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str | None = None

class Login(BaseModel):
    email: str
    password: str

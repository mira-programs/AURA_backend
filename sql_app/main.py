from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import crud, models, schemas

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/accounts/", response_model=schemas.Account)
def create_account(account: schemas.AccountCreate, db: Session = Depends(get_db)):
    db_account = crud.get_account_by_email(db, email=account.email)
    if db_account:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_account(db=db, user=account)

@app.get("/accounts/me/", response_model=schemas.Account)
def read_account_me(email: str, db: Session = Depends(get_db)):
    db_account = crud.get_account_by_email(db, email=email)
    if db_account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    return db_account

@app.get("/challenges/", response_model=list[schemas.Challenge])
def read_challenges(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return crud.get_challenges(db, skip=skip, limit=limit)

@app.post("/accounts/{account_id}/complete_challenge/{challenge_id}", response_model=schemas.Account)
def complete_challenge(account_id: int, challenge_id: int, db: Session = Depends(get_db)):
    db_account = crud.complete_challenge(db, account_id, challenge_id)
    if db_account is None:
        raise HTTPException(
            status_code=404,
            detail="Account or Challenge not found",
        )
    return db_account

@app.put("/accounts/{account_id}/username", response_model=schemas.Account)
def update_username(account_id: int, username_update: schemas.AccountUpdateUsername, db: Session = Depends(get_db)):
    db_account = crud.update_account_username(db, account_id, username_update.username)
    if db_account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    return db_account

@app.put("/accounts/{account_id}/email", response_model=schemas.Account)
def update_email(account_id: int, email_update: schemas.AccountUpdateEmail, db: Session = Depends(get_db)):
    db_account = crud.get_account_by_email(db, email=email_update.email)
    if db_account:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    db_account = crud.update_account_email(db, account_id, email_update.email)
    if db_account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    return db_account

from sqlalchemy.orm import Session
import models, schemas

def get_account(db: Session, id: int):
    return db.query(models.Account).filter(models.Account.id == id).first()

def get_account_by_email(db: Session, email: str):
    return db.query(models.Account).filter(models.Account.email == email).first()

def get_accounts(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Account).offset(skip).limit(limit).all()

def create_account(db: Session, user: schemas.AccountCreate):
    hashed_password = models.Account.hash_password(user.password)
    db_account = models.Account(email=user.email, hashed_password = hashed_password)
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account

def get_challenge(db: Session, id: int):
    return db.query(models.Challenge).filte(models.Challenge.id == id).first()

def get_challenges(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Challenge).offset(skip).limit(limit).all()

def complete_challenge(db: Session, account_id: int, challenge_id: int):
    db_account = get_account(db, account_id)
    db_challenge = get_challenge(db, challenge_id)
    if db_account and db_challenge:
        db_account.completed_challenges.append(db_challenge)
        db.commit()
        db.refresh(db_account)
        return db_account
    return None
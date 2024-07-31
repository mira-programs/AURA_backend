from sqlalchemy.orm import Session
import models, schemas

def get_account(db: Session, id: int):
    return db.query(models.Account).filter(models.Account.id == id).first()

def get_account_by_email(db: Session, email: str):
    return db.query(models.Account).filter(models.Account.email == email).first()

def get_accounts(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Account).offset(skip).limit(limit).all()

def create_account(db: Session, user: schemas.AccountCreate):
    db_account = models.Account(
        email=user.email,
        username=user.username,
        password=user.password,
        first_name=user.first_name,
        last_name=user.last_name
    )
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account

def delete_account(db: Session, account_id: int):
    db_account = db.query(models.Account).filter(models.Account.id == account_id).first()
    if db_account:
        db.delete(db_account)
        db.commit()
        return True
    return False

def update_account_username(db: Session, account_id: int, new_username: str):
    db_account = db.query(models.Account).filter(models.Account.id == account_id).first()
    if db_account:
        db_account.username = new_username
        db.commit()
        db.refresh(db_account)
    return db_account

def update_account_email(db: Session, account_id: int, new_email: str):
    db_account = db.query(models.Account).filter(models.Account.id == account_id).first()
    if db_account:
        db_account.email = new_email
        db.commit()
        db.refresh(db_account)
    return db_account

def get_challenge(db: Session, id: int):
    return db.query(models.Challenge).filter(models.Challenge.id == id).first()

def get_challenges(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Challenge).offset(skip).limit(limit).all()

def create_challenge(db: Session, challenge: schemas.ChallengeCreate):
    db_challenge = models.Challenge(description=challenge.description, points=challenge.points)
    db.add(db_challenge)
    db.commit()
    db.refresh(db_challenge)
    return db_challenge

def accept_challenge(db: Session, account_id: int, challenge_id: int):
    db_account = get_account(db, account_id)
    db_challenge = get_challenge(db, challenge_id)
    if db_account and db_challenge:
        db_challenge_status = models.AcceptedChallenge(
            account_id=account_id,
            challenge_id=challenge_id,
            completed=False,
            failed=False
        )
        db.add(db_challenge_status)
        db.commit()
        db.refresh(db_challenge_status)
        return db_challenge_status
    return None

def complete_challenge(db: Session, account_id: int, challenge_id: int):
    db_challenge_status = db.query(models.ChallengeStatus).filter(
        models.ChallengeStatus.account_id == account_id,
        models.ChallengeStatus.challenge_id == challenge_id
    ).first()
    if db_challenge_status:
        if db_challenge_status.failed:
            raise Exception("Challenge cannot be completed because it has already failed.")
        db_challenge_status.completed = True
        db.commit()  # This line should be db.commit(), not db.changes()
        db.refresh(db_challenge_status)
        db_account = get_account(db, account_id)
        db_account.points += db_challenge_status.challenge.points
        db.commit()
        return db_account
    return None

def fail_challenge(db: Session, account_id: int, challenge_id: int):
    db_challenge_status = db.query(models.AcceptedChallenge).filter(
        models.AcceptedChallenge.account_id == account_id,
        models.AcceptedChallenge.challenge_id == challenge_id
    ).first()
    if db_challenge_status:
        if db_challenge_status.completed:
            raise Exception("Challenge cannot be failed because it has already been completed.")
        db_challenge_status.failed = True
        db.changes()
        db.refresh(db_challenge_status)
        db_account = get_account(db, account_id)
        db_account.points -= db_challenge_status.challenge.points
        db.commit()
        return db_account
    return None

def get_friends(db: Session, account_id: int):
    account = db.query(models.Account).filter(models.Account.id == account_id).first()
    return account.friends if account else []

def search_accounts_by_username(db: Session, username: str):
    return db.query(models.Account).filter(models.Account.username.contains(username)).all()

def get_accounts_by_points(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Account).order_by(models.Account.points.desc()).offset(skip).limit(limit).all()

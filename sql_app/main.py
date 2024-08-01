from fastapi import FastAPI, HTTPException, Depends, File, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import google.generativeai as genai
import PIL.Image
from io import BytesIO
import textwrap
from database import SessionLocal, engine
import crud, models, schemas
from IPython.display import Markdown

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Hardcoded API Key
API_KEY = 'AIzaSyCnF3Z6RYjIhunH18AfYhj0Vkh2dEnBs4E'

# Configure Gemini API
genai.configure(api_key=API_KEY)

# Find a suitable model
model_name = None
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        model_name = m.name
        print(m.name)
        break

if model_name is None:
    raise ValueError("No suitable model found for content generation.")

model = genai.GenerativeModel(model_name)

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def to_markdown(text):
    text = text.replace('•', '  *')
    return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post('/predict')
async def predict(file: UploadFile = File(...), description: str = None):
    if description is None:
        raise HTTPException(status_code=400, detail="Challenge description is required")

    # Read image file
    contents = await file.read()
    img = PIL.Image.open(BytesIO(contents))

    # Prepare API request
    try:
        response = model.generate_content([description, {
            'mime_type': file.content_type,
            'data': contents
        }])
        markdown_text = to_markdown(response.text)
        return JSONResponse(content={'predictions': markdown_text})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

# CRUD operations for accounts
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

@app.get("/accounts/", response_model=list[schemas.Account])
def read_accounts(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return crud.get_accounts(db, skip=skip, limit=limit)

@app.delete("/accounts/{account_id}")
def delete_account(account_id: int, db: Session = Depends(get_db)):
    if not crud.delete_account(db, account_id):
        raise HTTPException(status_code=404, detail="Account not found")
    return {"detail": "Account deleted"}

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

@app.get("/challenges/", response_model=list[schemas.Challenge])
def read_challenges(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return crud.get_challenges(db, skip=skip, limit=limit)

@app.post("/challenges/", response_model=schemas.Challenge)
def create_challenge(challenge: schemas.ChallengeCreate, db: Session = Depends(get_db)):
    return crud.create_challenge(db, challenge)

@app.post("/accounts/{account_id}/accept_challenge/{challenge_id}", response_model=schemas.ChallengeStatus)
def accept_challenge(account_id: int, challenge_id: int, db: Session = Depends(get_db)):
    return crud.accept_challenge(db, account_id, challenge_id)

@app.post("/accounts/{account_id}/complete_challenge/{challenge_id}", response_model=schemas.Account)
def complete_challenge(account_id: int, challenge_id: int, db: Session = Depends(get_db)):
    return crud.complete_challenge(db, account_id, challenge_id)

@app.post("/accounts/{account_id}/fail_challenge/{challenge_id}", response_model=schemas.Account)
def fail_challenge(account_id: int, challenge_id: int, db: Session = Depends(get_db)):
    return crud.fail_challenge(db, account_id, challenge_id)

@app.get("/accounts/{account_id}/friends", response_model=list[schemas.Account])
def get_friends(account_id: int, db: Session = Depends(get_db)):
    return crud.get_friends(db, account_id)

@app.get("/accounts/search/", response_model=list[schemas.Account])
def search_accounts(username: str, db: Session = Depends(get_db)):
    return crud.search_accounts_by_username(db, username)

@app.get("/accounts/leaderboard", response_model=list[schemas.Account])
def get_leaderboard(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return crud.get_accounts_by_points(db, skip=skip, limit=limit)

@app.post("/accounts/{sender_id}/send_friend_request/{receiver_id}")
def send_friend_request(sender_id: int, receiver_id: int, db: Session = Depends(get_db)):
    try:
        return crud.send_friend_request(db, sender_id, receiver_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/accounts/{sender_id}/accept_friend_request/{receiver_id}")
def accept_friend_request(sender_id: int, receiver_id: int, db: Session = Depends(get_db)):
    try:
        return crud.accept_friend_request(db, sender_id, receiver_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/accounts/{sender_id}/reject_friend_request/{receiver_id}")
def reject_friend_request(sender_id: int, receiver_id: int, db: Session = Depends(get_db)):
    try:
        return crud.reject_friend_request(db, sender_id, receiver_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/accounts/{account_id}/sent_friend_requests")
def get_sent_friend_requests(account_id: int, db: Session = Depends(get_db)):
    return crud.get_sent_friend_requests(db, account_id)

@app.get("/accounts/{account_id}/received_friend_requests")
def get_received_friend_requests(account_id: int, db: Session = Depends(get_db)):
    return crud.get_received_friend_requests(db, account_id)

# Run the application
if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)

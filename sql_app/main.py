from fastapi import FastAPI, HTTPException, Depends, File, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import google.generativeai as genai
import PIL.Image
from io import BytesIO
import textwrap
from database import SessionLocal, engine
import crud, models, schemas
from transformers import GPT2Tokenizer, GPT2LMHeadModel, Trainer, TrainingArguments
from datasets import Dataset
import json
import pandas as pd
import logging
from fastapi.middleware.cors import CORSMiddleware

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # List of allowed origins (you can use ["*"] for all origins)
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

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

model = genai.GenerativeModel('gemini-1.5-flash')

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

@app.get("/test")
async def test_connection():
    return {"message": "Connection successful"}

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

@app.get("/accounts/{account_id}/get_challenge", response_model=schemas.Challenge)
def get_challenge_for_user(account_id: int, min_points: int, max_points: int, db: Session = Depends(get_db)):
    challenge = crud.get_available_challenge(db, account_id, min_points, max_points)
    if not challenge:
        raise HTTPException(status_code=404, detail="No available challenge found within the specified points range.")
    return challenge  

@app.post('/predict')
async def predict(file: UploadFile = File(...), description: str = None):
    if description is None:
        raise HTTPException(status_code=400, detail="Challenge description is required")

    # Read image file
    contents = await file.read()
    img = PIL.Image.open(BytesIO(contents))

    # Prepare API request
    try:
        response = model.generate_content([description + "respond with ONLY yes or no. does the image match the previous statement?", {
            'mime_type': file.content_type,
            'data': contents
        }])
        return JSONResponse(content={'predictions': response.text})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@app.post("/train_model")
def train_model():
    try:
        # Load your dataset
        with open('data/challenges.json') as f:
            data = json.load(f)

        # Convert to DataFrame
        df = pd.DataFrame(data)

        # Create a single string input for the model
        df['input'] = df.apply(lambda x: f"Challenge: {x['description']} Points: {x['points']}", axis=1)

        # Load tokenizer and model
        tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
        model = GPT2LMHeadModel.from_pretrained('gpt2')

        # Tokenize the data
        train_dataset = Dataset.from_pandas(df[['input']])
        train_dataset = train_dataset.map(lambda e: tokenizer(e['input'], truncation=True, padding='max_length'), batched=True)

        # Define training arguments
        training_args = TrainingArguments(
            output_dir='./results',
            num_train_epochs=3,
            per_device_train_batch_size=4,
            save_steps=10_000,
            save_total_limit=2,
        )

        # Initialize Trainer
        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=train_dataset,
        )

        # Train the model
        trainer.train()

        # Save the model
        model.save_pretrained('./model')
        tokenizer.save_pretrained('./model')

        return {"message": "Model trained and saved successfully"}
    except Exception as e:
        logger.error(f"Error training model: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@app.post("/generate_challenge", response_model=schemas.Challenge)
def generate_challenge():
    try:
        # Load tokenizer and model
        tokenizer = GPT2Tokenizer.from_pretrained('./model')
        model = GPT2LMHeadModel.from_pretrained('./model')

        # Generate a response
        input_prompt = "Generate a challenge description and assign a points value."
        inputs = tokenizer.encode(input_prompt, return_tensors='pt')

        outputs = model.generate(inputs, max_length=50, num_return_sequences=1)
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Parse the response to separate the description and points
        if ':' not in response:
            raise HTTPException(status_code=500, detail="Failed to generate a valid challenge.")
        
        description, points = response.split(':', 1)
        description = description.strip()
        points = points.strip()
        
        # Validate points
        try:
            points = int(points)
        except ValueError:
            raise HTTPException(status_code=500, detail="Failed to parse points value.")

        return {"description": description, "points": points}
    except Exception as e:
        logger.error(f"Error generating challenge: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

# Run the application
if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)

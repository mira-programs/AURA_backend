import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        logger.error(f"Training model failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

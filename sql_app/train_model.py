import json
import pandas as pd
from datasets import Dataset
from transformers import GPT2Tokenizer, GPT2LMHeadModel, Trainer, TrainingArguments

# Load your dataset
with open('data/challenges.json') as f:
    data = json.load(f)

# Convert to DataFrame
df = pd.DataFrame(data)

# Create a single string input for the model
df['input'] = df.apply(lambda x: f"Challenge: {x['challenge']} Points: {x['points']}", axis=1)

# Load tokenizer and model
tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
model = GPT2LMHeadModel.from_pretrained('gpt2')

# Tokenize the input data
dataset = Dataset.from_pandas(df[['input']])
dataset = dataset.map(lambda examples: tokenizer(examples['input'], padding='max_length', truncation=True, max_length=50), batched=True)
dataset.set_format(type='torch', columns=['input_ids', 'attention_mask'])

# Training arguments
training_args = TrainingArguments(
    output_dir='./results',
    num_train_epochs=3,
    per_device_train_batch_size=2,
    save_steps=10_000,
    save_total_limit=2,
)

# Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset
)

# Train the model
trainer.train()

# Save the model and tokenizer
model.save_pretrained('./results')
tokenizer.save_pretrained('./results')

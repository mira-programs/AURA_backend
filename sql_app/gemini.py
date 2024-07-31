import pathlib
import textwrap

import google.generativeai as genai
import PIL.Image

#from IPython.display import display
#from IPython.display import Markdown
#from google.colab import userdata

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from io import BytesIO
import os


app = FastAPI()

#img = PIL.Image.open('image.jpg')


# Or use `os.getenv('GOOGLE_API_KEY')` to fetch an environment variable.
#GOOGLE_API_KEY=userdata.get('AIzaSyCnF3Z6RYjIhunH18AfYhj0Vkh2dEnBs4E')


GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', 'AIzaSyCnF3Z6RYjIhunH18AfYhj0Vkh2dEnBs4E')

genai.configure(api_key=GOOGLE_API_KEY)


model_name = None
for m in genai.list_models():
  if 'generateContent' in m.supported_generation_methods:
        model_name = m.name
        print(m.name)
        break

if model_name is None:
    raise ValueError("No suitable model found for content generation.")


model = genai.GenerativeModel('gemini-1.5-flash')


def to_markdown(text):
  text = text.replace('•', '  *')
  return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))


@app.post('/predict')
async def predict(file: UploadFile = File(...)):
    contents = await file.read()
    img = PIL.Image.open(BytesIO(contents))
    response = model.generate_content(img)
    markdown_text = to_markdown(response.text)
    return JSONResponse(content={'predictions': markdown_text})

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
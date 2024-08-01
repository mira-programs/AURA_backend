from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import tensorflow as tf
from tensorflow.keras.applications.mobilenet_v2 import MobileNetV2, preprocess_input, decode_predictions
from tensorflow.keras.preprocessing import image
import numpy as np
from io import BytesIO

app = FastAPI()

# MobileNetV2 model: an AI model for image recognition, coming from TensorFlow
model = MobileNetV2(weights='imagenet')

@app.post('/')
async def home():
    return "hi"

@app.post('/predict')
async def predict(file: UploadFile = File(...)):
    contents = await file.read()
    img = image.load_img(BytesIO(contents), target_size=(224, 224))
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = preprocess_input(x)
    
    preds = model.predict(x)
    results = decode_predictions(preds, top=1)[0]
    print(results)

        # Converting the results to a JSON-serializable format
    serialized_results = []
    for result in results:
        serialized_results.append({
            'class': result[0],
            'label': result[1],
            'score': float(result[2])
        })
    print(serialized_results)
    
    return JSONResponse(content={'predictions': serialized_results})

  

if _name_ == '_main_':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
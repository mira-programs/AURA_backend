from flask import Flask, request, jsonify
import tensorflow as tf
from tensorflow.keras.applications.mobilenet_v2 import MobileNetV2, preprocess_input, decode_predictions
from tensorflow.keras.preprocessing import image
import numpy as np

app = Flask(__name__)

# MobileNetV2 model: an AI model for image recognition, coming from TensorFlow
model = MobileNetV2(weights='imagenet')

@app.route('/predict', methods=['POST'])
def predict():
    file = request.files['file']
    img = image.load_img(file, target_size=(224, 224))
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = preprocess_input(x)
    preds = model.predict(x)
    results = decode_predictions(preds, top=1)[0]
    return jsonify({ 'predictions': results })

if __name__ == '__main__':
    app.run(debug=True)

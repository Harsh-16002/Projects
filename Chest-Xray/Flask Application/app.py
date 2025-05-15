import os
import numpy as np
from PIL import Image
import cv2
from flask import Flask, request, render_template
from werkzeug.utils import secure_filename
from tensorflow.keras.models import load_model


app = Flask(__name__)

try:
    model = load_model('chest_xray_vgg19.keras')
    print("Model loaded successfully.")
except Exception as e:
    print(f"Error loading model: {e}")

print('Model loaded. Check http://127.0.0.1:5000/')

def get_className(classNo):
    if classNo == 0:
        return "Normal"
    elif classNo == 1:
        return "Pneumonia"


def getResult(img_path):
    try:
   
        image = cv2.imread(img_path)
        if image is None:
            return "Image not found or unable to read."

       
        image = cv2.resize(image, (224, 224)) 
        image = Image.fromarray(image, 'RGB')
        image = np.array(image)
        input_img = np.expand_dims(image, axis=0)
        
        
        result = model.predict(input_img)
        result01 = np.argmax(result, axis=1)[0]
        return result01
    except Exception as e:
        return f"Error in prediction: {e}"

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def upload():
    if request.method == 'POST':
        f = request.files['file']
        basepath = os.path.dirname(__file__)
        upload_dir = os.path.join(basepath, 'uploads')
        
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
        
        file_path = os.path.join(upload_dir, secure_filename(f.filename))
        f.save(file_path)
        
        value = getResult(file_path)  
        result = get_className(value)  

        
        if result:
            return result.strip().lower() 
        return "error"

    return None

if __name__ == '__main__':
    app.run(debug=True)

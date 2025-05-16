from flask import Flask, request, render_template, redirect, url_for, session, flash
import tensorflow as tf
from tensorflow.keras.utils import load_img, img_to_array
import numpy as np
from werkzeug.utils import secure_filename
import os
import uuid

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'  # Folder to store uploaded images
app.secret_key = "your_secret_key"  # Secret key for session management

# Allowed file extensions for uploads
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Load the pre-trained model
model = tf.keras.models.load_model(
    r"E:\Major Project\Flask_Application\model\vgg19_leaf_final_model.h5"
)

# Define class labels
class_labels = [
    "Alpinia Galanga (Rasna)", "Amaranthus Viridis (Arive-Dantu)", "Artocarpus Heterophyllus (Jackfruit)",
    "Azadirachta Indica (Neem)", "Basella Alba (Basair)", "Brassica Juncea (Indian Mustard)",
    "Carissa Carandas (Karanda)", "Citrus Limon (Lemon)", "Ficus Auriculata (Roxburgh fig)",
    "Ficus Religiosa (Peepal Tree)", "Hibiscus Rosa-sinensis", "Jasminum (Jasmine)",
    "Mangifera Indica (Mango)", "Mentha (Mint)", "Moringa Oleifera (Drumstick)",
    "Muntingia Calabura (Jamaica Cherry - Gasagase)", "Murraya Koenigii (Curry)", "Nerium Oleander (Oleander)",
    "Nyctanthes Arbor-tristis (Parijata)", "Ocimum Tenuiflorum (Tulsi)", "Piper Betle (Betel)",
    "Plectranthus Amboinicus (Mexican Mint)", "Pongamia Pinnata (Indian Beech)", "Psidium Guajava (Guava)",
    "Punica Granatum (Pomegranate)", "Santalum Album (Sandalwood)", "Syzygium Cumini (Jamun)",
    "Syzygium Jambos (Rose Apple)", "Tabernaemontana Divaricata (Crape Jasmine)",
    "Trigonella Foenum-graecum (Fenugreek)"
]

# Complete plant benefits dictionary
plant_benefits = {
    "Alpinia Galanga (Rasna)": "Used in traditional medicine for digestive issues, colds, and inflammation.",
    "Amaranthus Viridis (Arive-Dantu)": "Rich in vitamins and minerals; used to treat constipation and improve digestion.",
    "Artocarpus Heterophyllus (Jackfruit)": "High in antioxidants; supports immune health and digestion.",
    "Azadirachta Indica (Neem)": "Antibacterial and antifungal properties; used for skin care and dental health.",
    "Basella Alba (Basair)": "Rich in iron and vitamins; used to treat anemia and improve skin health.",
    "Brassica Juncea (Indian Mustard)": "Contains antioxidants; supports heart health and reduces inflammation.",
    "Carissa Carandas (Karanda)": "Used to treat diarrhea, fever, and skin diseases.",
    "Citrus Limon (Lemon)": "Rich in vitamin C; boosts immunity and aids digestion.",
    "Ficus Auriculata (Roxburgh fig)": "Used to treat diabetes, diarrhea, and respiratory issues.",
    "Ficus Religiosa (Peepal Tree)": "Used in Ayurveda for asthma, diabetes, and skin diseases.",
    "Hibiscus Rosa-sinensis": "Used to treat hair loss, high blood pressure, and liver disorders.",
    "Jasminum (Jasmine)": "Used for relaxation, stress relief, and skin care.",
    "Mangifera Indica (Mango)": "Rich in vitamins A and C; supports eye health and immunity.",
    "Mentha (Mint)": "Aids digestion, relieves headaches, and improves respiratory health.",
    "Moringa Oleifera (Drumstick)": "Rich in nutrients; boosts energy and supports overall health.",
    "Muntingia Calabura (Jamaica Cherry - Gasagase)": "Used to treat headaches, colds, and digestive issues.",
    "Murraya Koenigii (Curry)": "Rich in antioxidants; supports digestion and hair health.",
    "Nerium Oleander (Oleander)": "Toxic plant; used in traditional medicine with caution.",
    "Nyctanthes Arbor-tristis (Parijata)": "Used to treat fever, arthritis, and skin diseases.",
    "Ocimum Tenuiflorum (Tulsi)": "Boosts immunity, reduces stress, and supports respiratory health.",
    "Piper Betle (Betel)": "Used to improve digestion and treat respiratory issues.",
    "Plectranthus Amboinicus (Mexican Mint)": "Used to treat coughs, colds, and digestive issues.",
    "Pongamia Pinnata (Indian Beech)": "Used to treat skin diseases, arthritis, and inflammation.",
    "Psidium Guajava (Guava)": "Rich in vitamin C; supports digestion and immunity.",
    "Punica Granatum (Pomegranate)": "High in antioxidants; supports heart health and digestion.",
    "Santalum Album (Sandalwood)": "Used for skin care, relaxation, and treating urinary infections.",
    "Syzygium Cumini (Jamun)": "Helps control blood sugar levels and improves digestion.",
    "Syzygium Jambos (Rose Apple)": "Rich in vitamins; supports hydration and skin health.",
    "Tabernaemontana Divaricata (Crape Jasmine)": "Used to treat eye infections and skin diseases.",
    "Trigonella Foenum-graecum (Fenugreek)": "Supports digestion, reduces inflammation, and controls blood sugar."
}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == "admin" and password == "password123":
            session['logged_in'] = True
            flash("Login Successful!", "success")
            return redirect(url_for('start'))
        else:
            flash("Invalid Username or Password", "danger")

    return render_template('login.html')

@app.route('/start')
def start():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('start.html')

@app.route('/predict', methods=['POST'])
def predict():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if 'file' not in request.files:
        flash("No file part in the request!", "warning")
        return redirect(url_for('start'))

    file = request.files['file']
    if file.filename == '':
        flash("No file selected!", "warning")
        return redirect(url_for('start'))

    if file and allowed_file(file.filename):
        filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        img = load_img(file_path, target_size=(224, 224))
        img_array = img_to_array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)

        prediction = model.predict(img_array)
        predicted_class = np.argmax(prediction, axis=1)[0]
        predicted_label = class_labels[predicted_class]
        benefits = plant_benefits.get(predicted_label, "No benefits information available.")

        return render_template('result.html', result=predicted_label, image_path=file_path, benefits=benefits)
    else:
        flash("Invalid file type! Please upload an image (jpg, jpeg, png).", "danger")
        return redirect(url_for('start'))

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)

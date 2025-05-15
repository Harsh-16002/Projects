import warnings
from PIL import Image
warnings.filterwarnings('ignore')
import tensorflow as tf
from keras.models import load_model
from keras.applications.vgg16 import preprocess_input
import numpy as np
from keras.preprocessing import image
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog, QMessageBox

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(600, 400)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.frame = QtWidgets.QFrame(self.centralwidget)
        self.frame.setGeometry(QtCore.QRect(0, 0, 600, 400))
        self.frame.setStyleSheet("background-color: #035874;")
        self.frame.setObjectName("frame")
        
        # Title label
        self.label_2 = QtWidgets.QLabel(self.frame)
        self.label_2.setGeometry(QtCore.QRect(100, 50, 400, 50))
        font = QtGui.QFont()
        font.setPointSize(24)
        font.setBold(True)
        self.label_2.setFont(font)
        self.label_2.setStyleSheet("color: white;")
        self.label_2.setObjectName("label_2")

        # Result label
        self.result_label = QtWidgets.QLabel(self.frame)
        self.result_label.setGeometry(QtCore.QRect(100, 150, 400, 50))
        font.setPointSize(18)
        self.result_label.setFont(font)
        self.result_label.setStyleSheet("color: white;")
        self.result_label.setObjectName("result_label")

        # Upload button
        self.pushButton = QtWidgets.QPushButton(self.frame)
        self.pushButton.setGeometry(QtCore.QRect(100, 250, 150, 40))
        font.setPointSize(12)
        font.setBold(True)
        self.pushButton.setFont(font)
        self.pushButton.setStyleSheet("QPushButton{border-radius: 10px; background-color:#DF582C;}\nQPushButton:hover {background-color: #7D93E0;}")
        self.pushButton.setObjectName("pushButton")

        # Prediction button
        self.pushButton_2 = QtWidgets.QPushButton(self.frame)
        self.pushButton_2.setGeometry(QtCore.QRect(300, 250, 150, 40))
        font.setPointSize(12)
        font.setBold(True)
        self.pushButton_2.setFont(font)
        self.pushButton_2.setStyleSheet("QPushButton{border-radius: 10px; background-color:#DF582C;}\nQPushButton:hover {background-color: #7D93E0;}")
        self.pushButton_2.setObjectName("pushButton_2")

        MainWindow.setCentralWidget(self.centralwidget)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        self.pushButton.clicked.connect(self.upload_image)
        self.pushButton_2.clicked.connect(self.predict_result)

        # Load model once during UI setup
        self.model = load_model('chest_xray.keras')
        self.image_loaded = False  # To track if image is uploaded

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "PNEUMONIA Detection"))
        self.label_2.setText(_translate("MainWindow", "PNEUMONIA Detection App"))
        self.pushButton.setText(_translate("MainWindow", "Upload Image"))
        self.pushButton_2.setText(_translate("MainWindow", "Predict"))

    def upload_image(self):
        filename = QFileDialog.getOpenFileName()
        path = filename[0]
        if not path:
            QMessageBox.warning(self.centralwidget, "Warning", "Please upload an image.")
            return
        try:
            img_file = image.load_img(path, target_size=(224, 224))
            x = image.img_to_array(img_file)
            x = np.expand_dims(x, axis=0)
            img_data = preprocess_input(x)
            global result
            result = self.model.predict(img_data)
            self.image_loaded = True  # Mark that image has been uploaded
        except Exception as e:
            QMessageBox.critical(self.centralwidget, "Error", f"Error loading image: {str(e)}")
            self.image_loaded = False  # Reset if image failed to load

    def predict_result(self):
        if not self.image_loaded:
            QMessageBox.warning(self.centralwidget, "Warning", "Please upload an X-ray image first.")
            return

        prediction = np.argmax(result, axis=1)
        if prediction[0] == 0:  # Assuming 0 corresponds to Normal
            self.result_label.setText("Result: Normal")
        else:
            self.result_label.setText("Result: Affected by PNEUMONIA")

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

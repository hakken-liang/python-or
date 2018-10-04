from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtPrintSupport import *
from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import *

from imageai.Prediction import ImagePrediction

import pyttsx3

import os
import sys
import time

#自製辨識函數

def object_recognition():
    execution_path = os.getcwd()
    prediction = ImagePrediction()
    prediction.setModelTypeAsResNet()
    prediction.setModelPath(os.path.join(execution_path, "resnet50_weights_tf_dim_ordering_tf_kernels.h5"))
    prediction.loadModel()
    predictions, probabilities = prediction.predictImage(os.path.join(execution_path, "rabbit.jpg"), result_count=10)
    print("It is a",predictions[0])
    engine = pyttsx3.init()
    engine.say(predictions[0])
    engine.runAndWait()




class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.available_cameras = QCameraInfo.availableCameras()
        if not self.available_cameras:
            pass #quit

        self.status = QStatusBar()
        self.setStatusBar(self.status)


        self.save_path = ""

        self.viewfinder = QCameraViewfinder()
        self.viewfinder.show()
        self.setCentralWidget(self.viewfinder)

        # Set the default camera.
        self.select_camera(0)

        # Setup tools
        camera_toolbar = QToolBar("Camera")
        camera_toolbar.setIconSize(QSize(16, 16))
        self.addToolBar(camera_toolbar)

        photo_action = QAction(QIcon(os.path.join('images', 'camera1.png')), "拍照...", self)
        photo_action.setStatusTip("按此紐可以拍下目前的影像")
        photo_action.triggered.connect(self.take_photo)
        camera_toolbar.addAction(photo_action)

        change_folder_action = QAction(QIcon(os.path.join('images', 'folder.png')), "選擇殂存資料夾", self)
        change_folder_action.setStatusTip("更改拍攝照片儲存的位置")
        change_folder_action.triggered.connect(self.change_folder)
        camera_toolbar.addAction(change_folder_action)


        camera_selector = QComboBox()
        camera_selector.addItems([c.description() for c in self.available_cameras])
        camera_selector.currentIndexChanged.connect( self.select_camera )

        camera_toolbar.addWidget(camera_selector)


        self.setWindowTitle("NSAViewer")
        self.show()

    def select_camera(self, i):
        self.camera = QCamera(self.available_cameras[i])
        self.camera.setViewfinder(self.viewfinder)
        self.camera.setCaptureMode(QCamera.CaptureStillImage)
        self.camera.error.connect(lambda: self.alert(self.camera.errorString()))
        self.camera.start()

        self.capture = QCameraImageCapture(self.camera)
        self.capture.error.connect(lambda i, e, s: self.alert(s))
        self.capture.imageCaptured.connect(lambda d, i: self.status.showMessage("Image %04d captured" % self.save_seq))

        self.current_camera_name = self.available_cameras[i].description()
        self.save_seq = 0

    def take_photo(self):
        self.viewfinder.setContrast(100)
        #self.viewfinder.setBrightness(0)

        timestamp = time.strftime("%d-%b-%Y-%H_%M_%S")
        self.capture.capture(os.path.join(self.save_path, "%s-%04d-%s.jpg" % (
            self.current_camera_name,
            self.save_seq,
            timestamp
        )))
        self.save_seq += 1
        ####在此送所拍下的照片辨識---->呼叫一個執行的自製函數
        print("=============")
        object_recognition()

    def change_folder(self):
        path = QFileDialog.getExistingDirectory(self, "Snapshot save location", "")
        if path:
            self.save_path = path
            self.save_seq = 0

    def alert(self, s):
        """
        Handle errors coming from QCamera dn QCameraImageCapture by displaying alerts.
        """
        err = QErrorMessage(self)
        err.showMessage(s)


if __name__ == '__main__':

    app = QApplication(sys.argv)
    app.setApplicationName("NSAViewer")

    window = MainWindow()
    app.exec_()
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget
from PySide6.QtWidgets import QApplication,QGraphicsView, QGraphicsScene
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget,QPushButton,QGraphicsPixmapItem
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import Qt,QPointF
from PySide6 import QtCore

import struct
import cv2
import numpy as np


import keyboard
class MapWidget(QWidget):
    #the origin 
        
    #x, y from blue bottom right
    #x direction for the long way of the field
    #             Qt.KeepAspectRatio,  # Maintains aspect ratio
    #             Qt.SmoothTransformation  # High-quality scaling
    #         )
    def __init__(self, newImageWidth):#if alliance false = red, alliance true = blue
        super().__init__()
 

        layout = QVBoxLayout()
        #self.alignLayout = QVBoxLayout()

        self.scene =  QGraphicsScene(self)
        self.view = QGraphicsView(self.scene)
        self.idealImageWidth = newImageWidth
        self.view.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        meterToPixel = 60
        self.cam1X = 8 * meterToPixel
        self.cam1Y = 4 * meterToPixel
        self.cam1Z = 1 * meterToPixel
        self.cam1theta = 90 #in degrees
        self.cam2X = 8 * meterToPixel
        self.cam2Y = 4.5 * meterToPixel
        self.cam2Z = 1 * meterToPixel
        self.cam2theta = 90 #in degrees
        self.mapPixmap = QPixmap('./room.png')
        self.mapPixmap = self.mapPixmap.scaled(
                self.idealImageWidth,
                10000,
                Qt.KeepAspectRatio,  # Maintains aspect ratio
                Qt.SmoothTransformation  # High-quality scaling
            )

        self.cameraPixmap = QPixmap('./camera.png')
        self.objectPixmap = QPixmap('./object.png')
        if self.cameraPixmap.isNull():
            print("Failed to load robot image!")
        self.mapItem = QGraphicsPixmapItem()
        self.mapItem.setPixmap(self.mapPixmap)
        # if self.mapItem.isNull():
        #     self.setText("Failed to load map image!")

        center_x = self.mapPixmap.width() / 2
        center_y = self.mapPixmap.height() / 2
        self.mapItem.setTransformOriginPoint(center_x, center_y)

        
        map = self.scene.addItem(self.mapItem)
        self.robot = self.scene.addPixmap(self.cameraPixmap)
        self.robot.setTransformOriginPoint(0, self.cameraPixmap.height() / 2)#self.cameraPixmap.width() / 2
        self.robot.setPos(self.cam1Y,self.cam1X)

        self.robot2 = self.scene.addPixmap(self.cameraPixmap)
        self.robot2.setTransformOriginPoint(self.cameraPixmap.width() / 2, self.cameraPixmap.height() / 2)
        self.robot2.setPos(self.cam2Y,self.cam2X)
        self.object = self.scene.addPixmap(self.objectPixmap)
        self.object.setTransformOriginPoint(self.cameraPixmap.width() / 2, self.cameraPixmap.height() / 2)#self.cameraPixmap.width() / 2

        #map.setPos(QPointF(0,0))
        self.mapItem.setRotation(0)

        self.mapItem.setPixmap(self.mapPixmap)

        layout.addWidget(self.view)
        self.setLayout(layout)


        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)
        self.cap.set(cv2.CAP_PROP_EXPOSURE, -1000.0) 
        self.cameraItem = QGraphicsPixmapItem()

        self.cap2 = cv2.VideoCapture(1)
        self.cap2.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)
        self.cap2.set(cv2.CAP_PROP_EXPOSURE, -1000.0) 
        self.cameraItem2 = QGraphicsPixmapItem()

        self.scene.addItem(self.cameraItem)
        self.scene.addItem(self.cameraItem2)

        self.cameraItem.setPos(500,0)
        self.cameraItem2.setPos(500,300)

        self.angle = 0
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.displayStream)
        # self.timer.timeout.connect(self.testDisplay)
        self.timer.setSingleShot(True)
        self.timer.start(1)


      Meters, and Radians
    def hardMaths(self, cam1X,cam1Y, cam1Z, cam1Rot, objectThetaFromCam1, objectPhiFromCam1
                      , cam2X, cam2Y,cam2Z, cam2Rot, objectThetaFromCam2, objectPhiFromCam2)
        objectX = ???
        objectY = ???
        objectZ = ???


        return ([objectX,objectY,objectZ])

        
    def cameraStuff(self, frame,cameraItem,robot,camAngle):
        height, width, channels = frame.shape
        # if not ret:
        #     self.timer.start(1)
        grayImage = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        ret, blackAndWhiteImage = cv2.threshold(grayImage, 127, 255, 0)

        edgedImage = cv2.Canny(blackAndWhiteImage, 50, 150)

        contours, _ = cv2.findContours(edgedImage, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Loop through contours and detect circles
        for contour in contours:
            (x, y), radius = cv2.minEnclosingCircle(contour)
            center = (int(x), int(y))
            radius = int(radius)
            area = cv2.contourArea(contour)
            perimeter = cv2.arcLength(contour, True)
            if perimeter > 0:
                circularity = 4 * np.pi * (area / (perimeter * perimeter))
            else:
                circularity = 0
                # Filter based on circularity and area
                
                    #print (width/2-x,height/2-y)
            self.angle = ((width/2-x)/(width/2)*35)
            self.azimuth = ((height/2-y)/(height/2)*(47/2))

            cv2.circle(frame, center, radius, (0, 255, 0), 2)


            # Display the resulting frame
            #cv2.imshow('Input', frame)

            # Press 'q' to exit
            #if cv2.waitKey(1) & 0xFF == ord('q'):
             #   break
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        h, w, ch = frame.shape
        bytesPerLine = ch * w
        cvtToQtFormat = QImage(
            frame.data, w, h, bytesPerLine, QImage.Format_RGB888
        )
        cvtToQtFormat = cvtToQtFormat.scaled(500, 500, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        camViewPixmap = QPixmap.fromImage(cvtToQtFormat)

        cameraItem.setPixmap(camViewPixmap)
        robot.setRotation(-camAngle + self.angle)
        # Release the capture
        # cap.release()
        # cv2.destroyAllWindows()
    def displayStream(self):
        # Read a frame from the camera
        ret, frame = self.cap.read()
        ret, frame2 = self.cap2.read()
        self.cameraStuff(frame,self.cameraItem,self.robot,self.cam1theta)
        self.cameraStuff(frame2,self.cameraItem2,self.robot2,self.cam2theta)
        self.timer.start(1)


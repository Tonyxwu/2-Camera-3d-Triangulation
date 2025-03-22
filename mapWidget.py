from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget
from PySide6.QtWidgets import QApplication,QGraphicsView, QGraphicsScene
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget,QPushButton,QGraphicsPixmapItem
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import Qt,QPointF
from PySide6 import QtCore

import struct
import cv2
import numpy as np
import math

import keyboard
class MapWidget(QWidget):
    #the origin 
        
    #x, y from blue bottom right
    #x direction for the long way of the field
    #             Qt.KeepAspectRatio,  # Maintains aspect ratio
    #             Qt.SmoothTransformation  # High-quality scaling
    #         )
    def __init__(self, newImageWidth):
        super().__init__()
 

        layout = QVBoxLayout()
        #self.alignLayout = QVBoxLayout()

        self.scene =  QGraphicsScene(self)
        self.view = QGraphicsView(self.scene)
        self.idealImageWidth = newImageWidth
        self.view.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        meterToPixel = 60.0
        self.cam1X = 8 * meterToPixel
        self.cam1Y = 4 * meterToPixel
        self.cam1Z = 1 * meterToPixel
        self.cam1theta = 0.0 #in degrees
        self.cam2X = 8.5 * meterToPixel
        self.cam2Y = 4 * meterToPixel
        self.cam2Z = 1 * meterToPixel
        self.cam2theta = 0.0 #in degrees
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
        self.object.setTransformOriginPoint(self.cameraPixmap.width() / 2, self.cameraPixmap.height() / 2) #self.cameraPixmap.width() / 2

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




    # Meters and Degrees
    def hardMaths(self, cam1X, cam1Y, cam1Z, cam1Rot, objectThetaC1A, objectThetaC1B,
                        cam2X, cam2Y, cam2Z, cam2Rot, objectThetaC2A, objectThetaC2B):
        try:
            # convert absolute coordinates to relative position
            dx = cam2X - cam1X
            # for purposes of this project cam1Y=cam2Y
            dz = cam2Z - cam1Z

            # convert rel objectTheta from C1 -> abs objectTheta from normal in XY
            k1 = cam1Rot + objectThetaC1A
            k2 = cam2Rot + objectThetaC2A
            # solve system of equations for intersecting lines (XY -> X, Y)
            objectX = dx/(1-(math.tan(math.radians(k1))/math.tan(math.radians(k2))))
            objectYfromXY = objectX * math.tan(math.radians(k1))

            # solve system of equations for intersecting lines (YZ -> Y, Z)
            objectYfromYZ = dz/(math.tan(math.radians(objectThetaC2B))-math.tan(math.radians(objectThetaC1B)))
            objectZ = objectYfromYZ * math.tan(math.radians(objectThetaC1B))

            objectY = (objectYfromXY+objectYfromYZ)/2
            # moves origin (0,0,0) from CAM1 to defined gamefield origin
            return([objectX+cam1X, objectY+cam1Y, objectZ+cam1Z])
        except:
            return([-1,-1,-1])




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
            self.angle = ((width/2-x)/(width/2)*35.0)
            self.azimuth = ((height/2-y)/(height/2)*(47.5/2))

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


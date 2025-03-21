


"""
This file creates an empty window with the title "Hello World".
Run this file to see the window.
"""
import sys
from PySide6.QtWidgets import *
# from PySide6.QtWidgets import QApplication, QMainWindow
# from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget
# from PySide6.QtWidgets import QLabel, QHBoxLayout, QWidget

# from PySide6.QtWidgets import QGridLayout

from mapWidget import MapWidget
from PySide6.QtGui import QKeySequence, QShortcut

# Every UI has a MainWindows that contains everything. 
class GRT2025DriverUI(QMainWindow):


  # We setup the window's title, size, and show it.
  def __init__(self):
    super().__init__()
    self.setWindowTitle("GRT 2025 Driver UI")
    self.resize(1920, 600)
    self.setMaximumHeight(600)

    self.centralWidget = QWidget(self)#omagic
    self.mainLayout = QHBoxLayout(self)
    self.centralWidget.setLayout(self.mainLayout)
    self.setCentralWidget(self.centralWidget)
    
    self.mapWidget = MapWidget(548)

    # self.topRightWheel = wheelImage()
    # self.mainLayout.addWidget(self.topRightWheel,0,0)#y 
    self.mainLayout.addWidget(self.mapWidget)
    
    esc_shortcut = QShortcut(QKeySequence("Esc"), self)
    esc_shortcut.activated.connect(self.close)

    self.show()


# This is the tamplate to start the UI, just copy it.
if __name__ == "__main__":
  app = QApplication(sys.argv)
  window = GRT2025DriverUI()
  window.showFullScreen()
  window.setGeometry(0, 0, 1920, 780)

    # Replace this with the URL of your image stream
    # stream_url = "https://via.placeholder.com/800x600.png"

    # # Create and show the widget
    # viewer = ImageStreamWidget(stream_url, refresh_interval=1000)
    # viewer.resize(800, 600)
    # viewer.show()
  exited = False
  sys.exit(app.exec())
  exited = True
  print (exited)



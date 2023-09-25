import typing
from PyQt5 import QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys, os
from pathlib import Path
from PyQt5.QtWidgets import QWidget
from containers import *
from file_manager_ import *

class Window(QWidget):
     def __init__(self, parent, titlebar: TitleBar):
          super().__init__()
          self.parent = parent
          self.titlebar = titlebar 
          self.setObjectName("mainWidget")
          self.windowLayout = QHBoxLayout(self)
          self.windowLayout.setAlignment(Qt.AlignLeft)
          self.windowLayout.setContentsMargins(0,0,0,0)
          self.windowLayout.setSpacing(0)

          self.sideBar = SideBar()
          self.windowLayout.addWidget(self.sideBar)

          self.bodyFileContent = FileManager(self)
          self.windowLayout.addWidget(self.bodyFileContent)

          self.sideBar.favorites.itemClicked.connect(self.selectedDir)

     def selectedDir(self, item):
          if sys.platform == "linux":
               if item.text() == "Other Locations": print("Yes")
               else: 
                    directory = self.sideBar.favorites.favLinux[self.sideBar.favorites.currentIndex().row()][item.text()]["path"]
                    self.bodyFileContent.setDirectory(Path(directory)) 
                    self.pwd = str(self.bodyFileContent.fileModel.rootPath()).split("/")
                    self.titlebar.setLocatorDir(self.pwd)
                    
     def setLocatorDir(self, path):
          self.titlebar.setLocatorDir(path=path)

class MainWindow(QMainWindow):
     def __init__(self):
          QMainWindow.__init__(self)
          self.radius = 10
          # self.setGeometry(50,50,1200,600)
          self.resize(QSize(1200, 600))
          #self.setWindowFlag(Qt.FramelessWindowHint)
          self.setAttribute(Qt.WA_TranslucentBackground)
          self.setContentsMargins(0,0,0,0)
          self.setMinimumSize(400, 400)
          self.shadow = QGraphicsDropShadowEffect()
          self.shadow.setBlurRadius(10)
          self.shadow.setColor(QColor("#000"))
          self.shadow.setOffset(QPoint(10,10))
          self.setGraphicsEffect(self.shadow)
          
          # if self.isMaximized(): pass
          # else: self.showMaximized()

          self.stylesheet = open("./venus/venus_st.css")
          self.setStyleSheet(self.stylesheet.read())

          self.titlebar = TitleBar(self)
          self.addToolBar(self.titlebar)

          self.windowWidget = Window(self, self.titlebar)
          self.setCentralWidget(self.windowWidget)
          self.titlebar.mouseMoveEvent = self.MouseMoveEvent


     def mousePressEvent(self, event: QMouseEvent) -> None:
          self.dragPos = event.globalPos()
          pass

     def MouseMoveEvent(self, event: QMouseEvent) -> None:
          self.move(self.pos() + event.globalPos() - self.dragPos)
          self.dragPos = event.globalPos()
          event.accept()
          pass
     
     """
     # def resizeEvent(self, event):
     #      path = QPainterPath()
     #      rect = QRectF(self.rect()).adjusted(.5, .5, -1.5, -1.5)
     #      path.addRoundedRect(rect, self.radius, self.radius)
     #      region = QRegion(path.toFillPolygon(QTransform()).toPolygon())
     #      self.setMask(region)
     """

def Main():
     app = QApplication(sys.argv)
     app.styleHints().setShowShortcutsInContextMenus(True)
     clipboard = app.clipboard()
     Window = MainWindow()
     Window.show()
     sys.exit(app.exec_())
        
        
if __name__ == "__main__":
     Main()
          
          
          
          

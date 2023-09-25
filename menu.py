from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class AddContextMenu(QMenu):
     def __init__(self, parent: QWidget, width=150):
          super(AddContextMenu, self).__init__()
          self.parent = parent
          self.radius = 10
          self.menuWidth = width
          self.setStyleSheet(
     '''
     *{
          font-family:system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
     }
     QMenu{
          padding: 5px;
          background-color: rgba(63, 63, 63, 100%);
          font-size: 15px;
          border-radius: 10px;
          border-color: #fff;
          font-family:system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
     }
     QMenu:item{
          padding: 6;
          border-radius: 5px;
          background-color: transparent;
          margin: 2px 1px;
          color: #fff;
          min-width: 100%;
          width: 150px;
          font-weight: 300;
     }
     QMenu:separator{
          max-width: 200px;
          height: 1px;
          margin: 2px;
          background-color: rgb(80, 80, 80);
     }
     QMenu:item:selected{
          background-color: rgb(80, 80, 80);
     }
     #menuLabel{
          color: #fff;
          padding: 2px;
          font-size: 15px;
          font-weight: 350;
     }
     QMenu #toolBarButton{
          max-width: 30px;
          min-width: 30px;
          width: 30px;
          outline: none;
          padding: 5px;
          border: 1px solid rgba(76, 76, 76, 50%);
          background-color: transparent;
          border-radius: 5px;
          min-height: 23px;
          height: 23px;
     }
     QMenu #toolBarButton:hover{
          background-color: rgba(76, 76, 76, 70%);
     }'''
     )

     def resizeEvent(self, event):
          path = QPainterPath()
          rect = QRectF(self.rect()).adjusted(.5, .5, -1.5, -1.5)
          path.addRoundedRect(rect, self.radius, self.radius)
          region = QRegion(path.toFillPolygon(QTransform()).toPolygon())
          self.setMask(region)

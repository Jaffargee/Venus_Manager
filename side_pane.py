import typing
from PyQt5 import QtGui
from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import os
from pathlib import Path
import getpass
#from disk_managment import *
import shutil
import sys
import glob

class SidePane(QFrame):
     def __init__(self) -> None:
          super(SidePane, self).__init__()
          self.setContentsMargins(0,0,0,0)
          self.setMinimumWidth(50)
          self.resize(QSize(100, self.width()))
          
          self.sidepane = QVBoxLayout(self)
          self.sidepane.setContentsMargins(0,0,0,0)
          
          self.details_name = QLabel("Places & Devices")
          
          self.listWidget = ShotcutsList()
          
          self.sidepane.addWidget(self.details_name)
          self.sidepane.addWidget(self.listWidget)
          
          # Adding object name
          self.details_name.setObjectName("details_name")
          
          
class ShotcutsList(QListWidget):
     def __init__(self):
          super(ShotcutsList, self).__init__()
          self.setContentsMargins(0,0,0,0)
          
          self.setObjectName("sidepane_list")
          
          self.setAcceptDrops(True)
          self.setDragEnabled(True)
          self.setDropIndicatorShown(True)
          self.setDragDropMode(QAbstractItemView.DragDrop)
          

          self.setIconSize(QSize(25,25))
          
          self.addLisItem(QIcon("./global_icons/display.svg"), "Computer")
          self.setCurrentItem(self.addLisItem(QIcon("./global_icons/thunar.svg"), getpass.getuser()))
          self.addLisItem(QIcon("./global_icons/distributor-logo.png"), "Applications")
          self.addLisItem(QIcon("./Folder Icons/folder-teal-desktop.svg"), "Desktop")
          self.addLisItem(QIcon("./Folder Icons/folder-teal-documents.svg"), "Documents")
          self.addLisItem(QIcon("./Folder Icons/folder-teal_download.svg"), "Downloads")
          self.addLisItem(QIcon("./Folder Icons/folder-teal-images.svg"), "Pictures")
          self.addLisItem(QIcon("./Folder Icons/folder-teal-music.svg"), "Music")
          self.addLisItem(QIcon("./Folder Icons/folder-teal-video.svg"), "Videos")
          
#          for ch in range(65, 91):
#               m = str(chr(ch) + ":")
#               if os.path.exists(m):
#                    drive_ = SetDriveVolumeName(m)
#                   self.addLisItem(QIcon("./global_icons/drive-harddisk.svg"), GetDriveVolumeName(drive_))
                    
                    
     def addLisItem(self, icon: QIcon, label: str) -> QListWidgetItem:
          item = QListWidgetItem(self)
          item.setIcon(icon)
          item.setText(label)
          return item
     
     
     def dragEnterEvent(self, e: QDragEnterEvent) -> None:
          if e.mimeData().hasUrls():
               e.accept()
          else:
               e.ignore()

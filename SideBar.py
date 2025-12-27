from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import os
from pathlib import Path
import getpass
import sys
from menu import AddContextMenu
from gui_download import Window
import subprocess
from file_operations_api import file_api


class SideBar(QFrame):
     def __init__(self) -> None:
          super().__init__()
          self.setContentsMargins(0,0,0,0)
          self.setFixedWidth(240)
          self.setObjectName("sidebar")

          self.listLayout = QVBoxLayout(self)
          self.listLayout.setContentsMargins(0,0,0,0)
          self.listLayout.setSpacing(0)
          self.listLayout.setAlignment(Qt.AlignTop)

          self.favorites = ShortCuts()
          self.listLayout.addWidget(self.favorites)

class ShortCuts(QListWidget):
     def __init__(self):
          super(ShortCuts, self).__init__()
          self.setAcceptDrops(True)  # enable drag and drop functionality

          delegate = CategoryLabelDelegate(self)
          self.setItemDelegate(delegate)

          self.setIconSize(QSize(25,25))

          # Get default paths from API
          default_paths = file_api.get_default_paths()

          self.shortcuts = [
               {"icon": QIcon("./icons/home.svg"), "title": "Home", "path": default_paths["Home"]},
               {"icon": QIcon("./icons/desktop.svg"), "title": "Desktop", "path": default_paths["Desktop"]},
               {"icon": QIcon("./icons/file.svg"), "title": "Documents", "path": default_paths["Documents"]},
               {"icon": QIcon("./icons/download.svg"), "title": "Downloads", "path": default_paths["Downloads"]},
               {"icon": QIcon("./icons/music.svg"), "title": "Music", "path": default_paths["Music"]},
               {"icon": QIcon("./icons/gallery.svg"), "title": "Pictures", "path": default_paths["Pictures"]},
               {"icon": QIcon("./icons/video.svg"), "title": "Videos", "path": default_paths["Videos"]},
               {"icon": QIcon("./icons/trash.svg"), "title": "Trash", "path": default_paths["Trash"]},
          ]

          self.devices = {
               "Other Locations": QIcon("./icons/plus.svg")
          }

          for shortcut in self.shortcuts:
               self.addFavoriteDirectory(dirname=shortcut["title"], icon=shortcut["icon"], listwidget=self)

          for dirname, icon in self.devices.items():
               self.addFavoriteDirectory(dirname=dirname, icon=icon, listwidget=self)


     def addFavoriteDirectory(self, dirname: str, icon: QIcon, listwidget: QListWidget):
          dirItem = QListWidgetItem(listwidget)
          dirItem.setText(dirname)
          dirItem.setIcon(icon)
          listwidget.addItem(dirItem)
          return dirItem

class CategoryLabelDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        # Customize the appearance of category labels
        if index.data(Qt.ItemIsSelectable) == Qt.NoItemFlags:
            painter.save()
            painter.setPen(QPen(QColor(120, 120, 120)))
            painter.setFont(QFont("Arial", 14, QFont.Bold))
            painter.drawText(option.rect, Qt.AlignCenter, index.data())
            painter.restore()
        else:
            QStyledItemDelegate.paint(self, painter, option, index)


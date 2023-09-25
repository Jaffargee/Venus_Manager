import urllib.request
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys
import os
import requests
import threading
from urllib.parse import *
from pathlib import Path


class Window(QWidget):
     def __init__(self):
          super().__init__()
          self.setObjectName("downloadContainer")
          self.setWindowModality(Qt.ApplicationModal)
          self.setFixedSize(QSize(760, 600))
          self.setWindowTitle("Downloads")
          self.setContentsMargins(0,0,0,0)
          
          with open("./venus/venus_st.css", "r") as style:
               self.setStyleSheet(style.read())
          
          self.main_layout = QHBoxLayout(self)
          self.main_layout.setContentsMargins(0,0,0,0)
          
          self.sidepanel = SidePane()
          self.mainpanel = MainPane()
          
          # Adding Widgets to Side Pane
          self.main_layout.addWidget(self.sidepanel)
          self.main_layout.addWidget(self.mainpanel)
          
class SidePane(QFrame):
     def __init__(self):
          super().__init__()
          self.setContentsMargins(0,0,0,0)
          self.setMaximumWidth(200)
          self.setObjectName("sidepane_d")
          
          self.sidepane_panel = QVBoxLayout(self)
          self.sidepane_panel.setContentsMargins(0,0,0,0)
          
          self.side_label = QLabel("Tasks")
          self.side_label.setStyleSheet("font-size: 17px; color: #fff; font-family: sans-serfi; padding: 1px; margin: 2px;")
          
          # List Widget
          self.sidePaneList = QListWidget()
          self.sidePaneList.setObjectName("sidepane_list")
          
          # Adding widget to sidepane_panel
          self.sidepane_panel.addWidget(self.side_label)
          self.sidepane_panel.addWidget(self.sidePaneList)
          
          self.sidePaneList.setCurrentItem(self.addListItem(QIcon("./global_icons/classicmenu-indicator-dark.svg"), "Tasks"))
          self.addListItem(QIcon("./global_icons/download.svg"), "Downloads")
          
          
     def addListItem(self, icon: QIcon, text: str) -> QListWidgetItem:
          item = QListWidgetItem(self.sidePaneList)
          item.setIcon(icon)
          item.setText(text)
          return item

class MainPane(QFrame):
     def __init__(self):
          super().__init__()
          
          self.mainPaneLayout = QVBoxLayout(self)
          self.mainPaneLayout.setAlignment(Qt.AlignTop)
          
          self.linkinput = LinkInputPane(self.mainPaneLayout)
          
          self.mainPaneLayout.addWidget(self.linkinput)

class LinkInputPane(QFrame):
     def __init__(self, layout: QVBoxLayout):
          super().__init__()
          self.layout_ = layout
          self.setContentsMargins(0,0,0,0)
          self.setObjectName("locator_panel")
          self.hboxLayout = QHBoxLayout(self)
          
          self.input = QLineEdit()
          self.input.returnPressed.connect(self.startDownload)
          self.input.setObjectName("locator_input_pane")
          self.input.setPlaceholderText("Paste a link here to download a file")
          
          self.buttonShadow = QGraphicsDropShadowEffect()
          self.buttonShadow.setColor(QColor("#19191a"))
          self.buttonShadow.setBlurRadius(2.4)
          self.buttonShadow.setOffset(1,1)
          
          self.downloadButton = QPushButton("Download")
          self.downloadButton.setGraphicsEffect(self.buttonShadow)
          self.downloadButton.setObjectName("downloadButton")
          self.downloadButton.clicked.connect(self.startDownload)
          self.downloadButton.setCursor(QCursor(Qt.PointingHandCursor))
          self.downloadButton.setIcon(QIcon("./global_icons/download.svg"))
          self.downloadButton.setIconSize(QSize(23,23))
          
          self.hboxLayout.addWidget(self.input)          
          self.hboxLayout.addWidget(self.downloadButton)
          
     def startDownload(self):
          if self.input.text() != "":
               self.downloadProgress = DownloadProgressBarContainer(self.input)
               self.layout_.addWidget(self.downloadProgress)          
               connected = self.downloadProgress.Download()
               if connected: pass
               else: self.layout_.removeWidget(self.downloadProgress)
          
class DownloadProgressBarContainer(QFrame):
     def __init__(self, input: QLineEdit) -> None:
          super().__init__()
          self.input = input.text()
          self.setObjectName("progress_frame")
          # self.setStyleSheet("QFrame{background-color: red;" + "}")
          self.setMaximumHeight(76)
                              
          self.mainFormLayout = QFormLayout(self)
          
          self.progressLayout = QVBoxLayout()
          
          self.icon_label = QIcon("./global_icons/computer.svg")
          self.icon_button = QPushButton()
          self.icon_button.setObjectName("icon_button")
          self.icon_button.setIcon(self.icon_label)
          self.icon_button.setIconSize(QSize(30,30))
          
          self.itemDownloadTitle = QLabel("")
          self.progressBar = QProgressBar()
          self.progressBar.setObjectName("progress_bar")
          self.progressBar.setMaximum(100)
          self.downloadBytes = QLabel("")
          
          self.progressLayout.addWidget(self.itemDownloadTitle)
          self.progressLayout.addWidget(self.progressBar)
          self.progressLayout.addWidget(self.downloadBytes)
          
          self.cancel_download_button = QPushButton()
          self.cancel_download_button.setObjectName("cd_button")
          self.cancel_download_button.setCursor(Qt.PointingHandCursor)
          self.cancel_download_button.setIcon(QIcon("./icons/times.svg"))
          
          self.openInFolder = QPushButton()
          self.openInFolder.setObjectName("cd_button")
          self.openInFolder.setCursor(Qt.PointingHandCursor)
          self.openInFolder.clicked.connect(self.printDownloadedItemDetails)
          self.openInFolder.setIcon(QIcon("./Folder Icons/folder-teal-open.svg"))
          self.openInFolder.setIconSize(QSize(20,20))
          
          self.center_p = QHBoxLayout()
          self.center_p.setContentsMargins(0,0,0,0)
          
          self.center_p.addLayout(self.progressLayout)
          
          self.isDone = False          
          
          self.mainFormLayout.addRow(self.icon_button, self.center_p)
          
          self.url = ""
          self.filesize = ""
          
          self.downloadItemDetails = {}
          
          self.setContextMenuPolicy(Qt.CustomContextMenu)
          self.customContextMenuRequested.connect(self.contextMenu)

     def get_file_size(self):
          try:
               if self.url.startswith("http"):
                    response = requests.head(self.url)
                    if response.status_code == 200:
                         content_length = response.headers.get('content-length')
                         if content_length:
                              self.downloadItemDetails["file-type"] = response.headers.get("Content-type") 
                              self.downloadItemDetails["file-size"] = int(content_length)
                              self.downloadItemDetails["Date"] = response.headers.get("Date") 
                              size_in_bytes = int(content_length)
                              size_in_kb = size_in_bytes / 1024
                              size_in_mb = size_in_kb / 1024
                              return size_in_mb
                    return 0
               else: pass
          except Exception as e: print(e)
     
     def setUrl(self, url):
          self.url = url
          self.downloadItemDetails["file-url"] = self.url
          
     def setFileSize(self, size):
          self.filesize = size
     
     def Handle_Progress(self, blocknum, blocksize, totalsize):
          # calculate the progress
          readed_data = blocknum * blocksize          
          
          if totalsize > 0:
               download_percentage = readed_data * 100 / totalsize
               if download_percentage >= 100:
                    self.isDone = True
                    if self.isDone:
                         self.center_p.addWidget(self.openInFolder)
                         self.progressBar.setHidden(True)
                         self.downloadBytes.setText("Complete. {:.2f}".format(self.filesize))
                         
               if readed_data > 1024:
                    size = self.convertToMB(readed_data)
                    self.downloadBytes.setText("{} MB / {:.2f} MB".format(size, self.filesize))
                    size = int(size.split(".")[0])
                    if size > 1024:
                         size = self.convertToGB(size)
                         self.downloadBytes.setText("{} GB / {:.2f} GB".format(size, self.filesize / 1024))
                         
               self.progressBar.setValue(int(download_percentage))
               
               QApplication.processEvents()
                             
     def Download(self):
          # specify save location where the file is to be saved
          file_name = unquote(self.input.split("/")[-1])
          self.downloadItemDetails["filename"] = file_name
          if len(file_name) > 45:
               file_name2 = file_name[0:45] + "..."
               self.itemDownloadTitle.setText(file_name2)
          else: self.itemDownloadTitle.setText(file_name)
          save_loc = f'./Downloads/{unquote(file_name)}'
          path = os.path.abspath(save_loc)
          self.downloadItemDetails["file-path"] = path
          self.setUrl(self.input)
          self.setFileSize(self.get_file_size())
          
          # Downloading using urllib
          try:
               if self.input.startswith("http"):
                    down, http = urllib.request.urlretrieve(self.input, save_loc, self.Handle_Progress)
                    if http:
                         return True
               else:
                    self.show_dialog("URL Error", "Please put valid URL")
                    return False
          except: self.show_dialog("Connection Error", "Cant't Connect to Server")
               
     def convertToMB(self, readed_data):
          sizeInKB = readed_data / 1024
          sizeInMB = sizeInKB / 1024
          return "{:.2f}".format(sizeInMB)
     
     def convertToGB(self, readed_data):
          sizeInGB = readed_data / 1024
          return "{:.2f}".format(sizeInGB)
               
     def show_dialog(self, title, msg) -> int:
        dialog = QMessageBox(self)
        dialog.setFixedWidth(500)
        dialog.setObjectName("messageBox")
        dialog.setWindowTitle(title)
        dialog.setWindowIcon(QIcon("./global-icons/edit-delete.png"))
        dialog.setText(msg)
        dialog.setStandardButtons(QMessageBox.Ok)
        dialog.setDefaultButton(QMessageBox.Ok)
        dialog.setIcon(QMessageBox.Warning)
        return dialog.exec_()

     def printDownloadedItemDetails(self):
          for key, value in self.downloadItemDetails.items():
               print("{}: \t {}".format(key, value))            

     def contextMenu(self, pos: QPoint):
          menu =  QMenu()
          menu.setObjectName("menu")
          styleSheet = open("./venus/qss/venus_st.css")
          menu.setStyleSheet(styleSheet.read())
          
          # Menu Actions
          self.copy_linkURl = QAction("Copy download link")
          self.openFile = QAction("Open file")
          self.deleteFile = QAction("Delete file")
          self.removeFile = QAction("Remove file")
          self.showInFolder = QAction("Show in folder")
          self.alwaysOpenFileType = QAction("Always open files of this type")
          
          menu.addActions([self.openFile, self.alwaysOpenFileType])
          menu.addSeparator()
          menu.addActions([self.showInFolder, self.copy_linkURl])
          menu.addSeparator()
          menu.addActions([self.deleteFile, self.removeFile])
          
          self.copy_linkURl.triggered.connect(self.copyDownloadLink)
          self.openFile.triggered.connect(self.openFileMethod)
          self.deleteFile.triggered.connect(self.deleteFileMethod)
          
          action = menu.exec_(self.mapToGlobal(pos))
          
          
          
     def copyDownloadLink(self):
          QApplication.clipboard().setText(self.downloadItemDetails["file-url"])
          
     def openFileMethod(self):
          os.startfile(self.downloadItemDetails["file-path"])
          
     def deleteFileMethod(self):
          path = Path(self.downloadItemDetails["file-path"])
          path.unlink()
          
          
          
          
          
          
          
          
          
          
          

def main():
     app = QApplication([])
     window = Window()
     window.show()
     sys.exit(app.exec_())
     
     
main()
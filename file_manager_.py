import typing
from PyQt5 import QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import os
from pathlib import Path
import shutil
import getpass
import sys
import json
from menu import AddContextMenu

class FileIcon(QFileIconProvider):
     def icon(self, fileinfo):
          if fileinfo.isDir():
               if fileinfo.fileName() == "Desktop":
                    return QIcon("./Folder Icons/folder-teal-desktop.svg")
               if fileinfo.fileName() == "Documents":
                    return QIcon("./Folder Icons/folder-teal-documents.svg")
               if fileinfo.fileName() == "Downloads":
                    return QIcon("./Folder Icons/folder-teal_download.svg")
               if fileinfo.fileName() == "Pictures":
                    return QIcon("./Folder Icons/folder-teal-images.svg")
               if fileinfo.fileName() == "Music":
                    return QIcon("./Folder Icons/folder-teal-music.svg")
               if fileinfo.fileName() == "Videos":
                    return QIcon("./Folder Icons/folder-teal-video.svg")
               if fileinfo.fileName() == getpass.getuser():
                    return QIcon("./Folder Icons/folder-teal-home.svg")
               return QIcon("./Folder Icons/folder-teal.svg")
          return QFileIconProvider.icon(self, fileinfo)

class FileManager(QListView):
     def __init__(self, parent) -> None:
          super(FileManager, self).__init__()
          self.parent = parent
          self.setObjectName("FileManager")
          self.setIconSize(QSize(30,30))
                    
          if sys.platform == "linux":
               self.location_path = f"/home/{getpass.getuser()}/Documents/Coding"
          else: self.location_path = f"C:/Users/{getpass.getuser()}"
          
          # Initializing Model
          self.fileModel = QFileSystemModel(self)
          self.fileModel.setRootPath(self.location_path)
          self.fileModel.setReadOnly(False)
          self.fileModel.setIconProvider(FileIcon())
          self.fileModel.setFilter(QDir.NoDotAndDotDot | QDir.AllDirs | QDir.Files | QDir.Drives)
          
          # Adding Model to the Tree View
          self.setModel(self.fileModel)
          self.setRootIndex(self.fileModel.index(self.fileModel.rootPath()))
          
          # Working with Icon
          self.setEditTriggers(QListView.EditTrigger.NoEditTriggers)
          self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
          self.setContextMenuPolicy(Qt.CustomContextMenu)
          self.customContextMenuRequested.connect(self.show_context_menu)
          
          self.setAcceptDrops(True)
          self.setDragEnabled(True)
          self.setDropIndicatorShown(True)
          self.setDragDropMode(QAbstractItemView.DragDrop)

          self.doubleClicked.connect(self.selectedToOpenDir)


     def show_context_menu(self, pos: QPoint):
          ix = self.indexAt(pos)
          self.contextMenu = AddContextMenu(self)
          self.newFolder = QAction("New Folder",self)
          self.openInConsole = QAction("Open in Terminal", self)
          self.pasteFile = QAction("Paste")
          self.selectAllContents = QAction("Select All")
          self.propertiesAction = QAction("Properties")

          self.newFolder.setShortcut("Ctrl+Shift+N")
          self.selectAllContents.setShortcut("Ctrl+A")
          self.pasteFile.setShortcut("Ctrl+P")

          self.openFolderFile = AddContextMenu("Open")
          self.openFolderFile.setTitle("Open")

          # OPEN FOLDER FILE CONTENTS
          self.openCurrent = QAction("Open")
          self.openCurrent.triggered.connect(self.getSelectedItems)
          self.openInNewWindow = QAction("Open New Window")
          self.openInNewTab = QAction("Open New Tab")

          self.openInNewTab.setShortcut("Ctrl+Alt+T")
          self.openInNewWindow.setShortcut("Ctrl+Alt+W")

          self.openFolderFile.addAction(self.openCurrent)
          self.openFolderFile.addAction(self.openInNewWindow)
          self.openFolderFile.addAction(self.openInNewTab)


          # FILE OPERATIONS, CUT, COPY, MOVE TO, COPY TO
          self.cutFileFolder = QAction("Cut", self)
          self.copyFileFolder = QAction("Copy",self)
          self.movetoFileFolder = QAction("Move to...", self)
          self.copytoFileFolder = QAction("Copy to...", self)

          # RENAME, CREATE A LINK, COMPRESS, MOVE TO TRASH
          self.renameFileFolders = QAction("Rename...", self)
          self.createLinkFileFolder = QAction("Create a Link", self)
          self.compressFileFolder = QAction("Compress...", self)
          self.movetoTrash = QAction("Move to Trash", self)

          self.renameFileFolders.triggered.connect(lambda: self.renameFileFolder(ix))
          self.newFolder.triggered.connect(self.openCreationDialog)
          self.movetoTrash.triggered.connect(lambda: self.action_delete(ix))
          # PROPERTIES
          self.properties = QAction("Properties")

          self.renameFileFolders.setShortcut("F2")
          self.cutFileFolder.setShortcut("Ctrl+X")
          self.copyFileFolder.setShortcut("Ctrl+X")
          self.compressFileFolder.setShortcut("Ctrl+Shift+M")
          self.properties.setShortcut("Alt+Return")

          if ix.column() == 0:
               self.contextMenu.addMenu(self.openFolderFile)
               self.contextMenu.addSeparator()
               self.contextMenu.addActions([self.cutFileFolder, self.copyFileFolder, self.movetoFileFolder, self.copytoFileFolder, self.movetoFileFolder])
               self.contextMenu.addSeparator()
               self.contextMenu.addActions([self.renameFileFolders, self.createLinkFileFolder, self.compressFileFolder, self.movetoTrash])
               self.contextMenu.addSeparator()
               self.contextMenu.addAction(self.properties)
          else:
               self.contextMenu.addActions([self.newFolder, self.openInConsole])
               self.contextMenu.addSeparator()
               self.contextMenu.addActions([self.pasteFile, self.selectAllContents])
               self.contextMenu.addSeparator()
               self.contextMenu.addAction(self.propertiesAction)

          self.action = self.contextMenu.exec_(self.viewport().mapToGlobal(pos))

          if not self.action:
               return

 
     def selectedToOpenDir(self, index: QModelIndex):
          path = self.fileModel.filePath(index)
          path = Path(path)
          if path.is_dir():
               self.setDirectory(path)
               self.parent.setLocatorDir(self.fileModel.rootPath().split("/"))

     def openCreationDialog(self):
          self.creationFolderDialog = Creation(self)
          self.creationFolderDialog.exec_()

     def setDirectory(self, path: Path):
          self.fileModel.setRootPath(str(path))
          self.setRootIndex(self.fileModel.index(self.fileModel.rootPath()))

     def getWorkingDirectory(self):
          pwd = self.fileModel.rootPath()
          return pwd

     def createFolder(self, folderName: str):
          if folderName != "":
               path = Path(self.fileModel.rootPath())/folderName
               count = 1
               while path.exists():
                    abspath = Path(path.parent / f"{path.parent}{count}")
                    count += 1
               idx = self.fileModel.mkdir(self.rootIndex(), path.name)
               self.creationFolderDialog.closeDialog()
               pwd = self.getWorkingDirectory() + f"/{path.name}"
               print(pwd)
               # self.setDirectory(Path(pwd))
          else: pass

     def renameFileFolder(self, ix: QModelIndex):
          self.edit(ix)

     def delete_file(self, path: Path):
          if path.is_dir():
               shutil.rmtree(path)
          else:
               path.unlink()

     def action_delete(self, ix):
          # check if selection
          file_name = self.fileModel.fileName(ix)
          dialog = self.show_dialog(
               "Delete", f"Are you sure you want to delete {file_name}"
          )
          if dialog == QMessageBox.Yes:
               if self.selectionModel().selectedIndexes():
                    for i in self.getSelectedItems():
                         path = Path(i)
                         self.delete_file(path)

     def show_dialog(self, title, msg) -> int:
          dialog = QMessageBox(self)
          dialog.font().setPointSize(14)
          dialog.setWindowTitle(title)
          dialog.setWindowIcon(QIcon("./icons/cancel.svg"))
          dialog.setText(msg)
          dialog.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
          dialog.setDefaultButton(QMessageBox.No)
          dialog.setIcon(QMessageBox.Warning)
          return dialog.exec_()
     
     def getSelectedItems(self):
          selected_indexes = self.selectedIndexes()
          selected_items = []
          for index in selected_indexes:
               file_info = self.fileModel.fileInfo(index)
               selected_items.append(file_info.absoluteFilePath())
          return selected_items



class Creation(QDialog):
     def __init__(self, parent: FileManager):
          super().__init__()
          self.parent = parent
          # self.setAttribute(Qt.WA_TranslucentBackground)
          self.setWindowModality(Qt.ApplicationModal)
          self.setWindowFlags(Qt.FramelessWindowHint)
          self.setContentsMargins(0,0,0,0)
          self.setObjectName("creationModal")
          self.radius = 10

          self.shadow = QGraphicsDropShadowEffect()
          self.shadow.setBlurRadius(2.0)
          self.shadow.setOffset(QPoint(6, 0))
          self.shadow.setColor(QColor("#000"))

          css = open("./venus/venus_st.css", "r")
          self.setStyleSheet(css.read())

          self.dialog = QFrame(self)
          self.dialog.setMinimumSize(500, 150)
          # self.dialog.setStyleSheet("border-radius: 7px; background-color: #fff;")

          self.mainLayout = QVBoxLayout(self.dialog)
          self.mainLayout.setAlignment(Qt.AlignTop)
          self.mainLayout.setContentsMargins(0,0,0,0)

          self.titleBar = QFrame()
          self.titleBar.setObjectName("titleBar")
          self.titleBar.setContentsMargins(0,0,0,0)
          self.titleBarLayout = QHBoxLayout(self.titleBar)
          self.titleBarLayout.setContentsMargins(0,0,0,0)

          self.cancelButton = QPushButton("Cancel")
          self.cancelButton.setObjectName("titleBarCancelButton")

          self.createButton = QPushButton("Create")
          self.createButton.setObjectName("titleBarCreateButton")
          self.createButton.setEnabled(False)

          self.cancelButton.setCursor(QCursor(Qt.PointingHandCursor))
          self.createButton.setCursor(QCursor(Qt.PointingHandCursor))

          self.titleBarLabel = QLabel("New Folder")
          self.titleBarLabel.setAlignment(Qt.AlignCenter)
          
          self.titleBarLayout.addWidget(self.cancelButton)
          self.titleBarLayout.addWidget(self.titleBarLabel)
          self.titleBarLayout.addWidget(self.createButton)

          self.pathInputLabel = QLabel("Folder Name")
          self.pathInputLabel.setStyleSheet("color: #fff; font-weight: 300; margin: 0px 10px; padding: 1px;")

          self.pathInput = QLineEdit()
          self.pathInput.setObjectName("path-input")
          self.pathInput.setFocus()

          self.cancelButton.clicked.connect(self.closeDialog)
          self.createButton.clicked.connect(lambda: parent.createFolder(self.pathInput.text()))
          self.pathInput.returnPressed.connect(lambda: parent.createFolder(self.pathInput.text()))
          self.pathInput.textEdited.connect(self.activateCreateButton)

          self.centerLayout = QVBoxLayout()

          self.mainLayout.addWidget(self.titleBar, alignment=Qt.AlignTop)
          self.centerLayout.addWidget(self.pathInputLabel)
          self.centerLayout.addWidget(self.pathInput)
          self.mainLayout.addLayout(self.centerLayout)

          layout = QVBoxLayout(self)
          layout.setContentsMargins(0,0,0,0)
          layout.addWidget(self.dialog)
          self.setWindowTitle("New Folder")


     def resizeEvent(self, event):
          path = QPainterPath()
          rect = QRectF(self.rect()).adjusted(.5, .5, -1.5, -1.5)
          path.addRoundedRect(rect, self.radius, self.radius)
          region = QRegion(path.toFillPolygon(QTransform()).toPolygon())
          self.setMask(region)

     def closeDialog(self):
          self.close()

     def activateCreateButton(self):
          if self.pathInput.text() != "":
               self.createButton.setEnabled(True)
          else: self.createButton.setDisabled(True)
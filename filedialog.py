from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from SideBar import SideBar
import sys, os
from pathlib import Path
import subprocess

class FileDialog(QDialog):
    def __init__(self, path):
        super().__init__()

        self.path = path
        self.type_ = "copy"

        self.setContentsMargins(0,0,0,0)
        self.setFixedSize(QSize(750, 350))
        self.setWindowTitle(f"Select Copy Destination")
        self.setObjectName("filedialog")
        css = open("venus/venus_st.css", "r")
        self.setStyleSheet(css.read())

        self.mainLayout = QVBoxLayout(self)
        self.mainLayout.setContentsMargins(0,0,0,0)

        self.hbox = QHBoxLayout()
        self.hbox.setContentsMargins(0,0,0,0)

        self.sidebar = SideBar()
        self.file = FileManager(self, self.path)

        self.sidebar.favorites.itemClicked.connect(self.selectedDir)

        self.hbox.addWidget(self.sidebar)
        self.hbox.addWidget(self.file)

        self.bottomPanel = QFrame()
        self.bottomPanel.setObjectName("bottomPanel")
        self.bottomPanelLayout = QHBoxLayout(self.bottomPanel)
        self.bottomPanelLayout.setContentsMargins(0,0,0,0)

        self.cancelButton = QPushButton("Cancel")
        self.selectButton = QPushButton("select")

        self.cancelButton.setCursor(Qt.PointingHandCursor)
        self.selectButton.setCursor(Qt.PointingHandCursor)

        self.cancelButton.setObjectName("bottomButton")
        self.selectButton.setObjectName("bottomButton")

        self.cancelButton.clicked.connect(self.closeWindow)

        self.bottomPanelLayout.addStretch()
        self.bottomPanelLayout.addWidget(self.cancelButton)
        self.bottomPanelLayout.addWidget(self.selectButton)

        self.mainLayout.addLayout(self.hbox)
        self.mainLayout.addWidget(self.bottomPanel)

    def selectedDir(self, item):
        item_text = item.text()
        if item_text == "Other Locations":
            self.file.setDirectory(Path("/" if sys.platform == "linux" else "C:/"))
        else:
            # Find the shortcut with matching title
            for shortcut in self.sidebar.favorites.shortcuts:
                if shortcut["title"] == item_text:
                    self.file.setDirectory(Path(shortcut["path"]))
                    break

    def execute(self, type_):
          self.type_ = type_
          self.exec_()
          self.setWindowModality(Qt.ApplicationModal)

    def getType(self): return self.type_

    def closeWindow(self):
        self.close()

class FileManager(QListView):
    def __init__(self, parent, path) -> None:
          super(FileManager, self).__init__()
          self.parent = parent
          self.path = path
          self.setObjectName("FileManager")
          self.setIconSize(QSize(30,30))

          # Initializing Model
          self.fileModel = QFileSystemModel(self)
          self.fileModel.setRootPath(self.path)
          self.fileModel.setReadOnly(False)
          self.fileModel.setFilter(QDir.NoDotAndDotDot | QDir.AllDirs | QDir.Files | QDir.Drives)
          
          # Adding Model to the Tree View
          self.setModel(self.fileModel)
          self.setRootIndex(self.fileModel.index(self.fileModel.rootPath()))
          
          # Working with Icon
          self.setEditTriggers(QListView.EditTrigger.NoEditTriggers)
          self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
          self.setContextMenuPolicy(Qt.CustomContextMenu)

          self.doubleClicked.connect(self.selectedToOpenDir)

    def selectedToOpenDir(self, index: QModelIndex):
        path = self.fileModel.filePath(index)
        path = Path(path)
        if path.is_dir():
            self.setDirectory(path)
        else:
            self._open_file(str(path))

    def _open_file(self, file_path: str):
        """Cross-platform file opening"""
        try:
            if sys.platform == "win32":
                os.startfile(file_path)
            elif sys.platform == "darwin":  # macOS
                subprocess.run(['open', file_path], check=True)
            else:  # Linux and other Unix-like
                subprocess.run(['xdg-open', file_path], check=True)
        except (OSError, subprocess.CalledProcessError) as e:
            print(f"Could not open file: {file_path} - {e}")

    def setDirectory(self, path: Path):
        self.fileModel.setRootPath(str(path))
        self.setRootIndex(self.fileModel.index(self.fileModel.rootPath()))
        # self.parent.setInputPath()

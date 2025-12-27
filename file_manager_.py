from PyQt5.QtWidgets import *
import PyQt5
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import os
from pathlib import Path
import shutil
import getpass
import sys
import json
import time
from menu import AddContextMenu
from urllib.parse import quote, unquote
import subprocess
from filedialog import FileDialog
from file_operations_api import file_api
from encryption_api import encryption_api
from trash_api import trash_api

class FileManager(QListView):
     def __init__(self, parent, path) -> None:
          super(FileManager, self).__init__()
          self.parent = parent
          self.setObjectName("FileManager")
          self.setIconSize(QSize(30,30))
          self.setViewMode(1)
                    
          if sys.platform == "linux":
               self.location_path = path
          else: self.location_path = f"C:/Users/{getpass.getuser()}"
          
          # Navigation history
          self.history = [self.location_path]
          self.current_history_index = 0
          
          # Initializing Model
          self.fileModel = QFileSystemModel(self)
          self.fileModel.setRootPath(self.location_path)
          self.fileModel.setReadOnly(False)
          self.fileModel.setFilter(QDir.NoDotAndDotDot | QDir.AllDirs | QDir.Files | QDir.Drives)
          
          # Proxy model for search filtering
          self.proxyModel = QSortFilterProxyModel(self)
          self.proxyModel.setSourceModel(self.fileModel)
          self.proxyModel.setFilterCaseSensitivity(Qt.CaseInsensitive)
          
          self.filedialog = FileDialog(self.fileModel.rootPath())
          self.filedialog.selectButton.clicked.connect(lambda: self.copyMovePathMethod(self.filedialog.getType()))
          
          # Adding Model to the Tree View
          self.setModel(self.proxyModel)
          self.setRootIndex(self.proxyModel.mapFromSource(self.fileModel.index(self.fileModel.rootPath())))
          
          # Working with Icon
          self.setEditTriggers(QListView.EditTrigger.NoEditTriggers)
          self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
          self.setContextMenuPolicy(Qt.CustomContextMenu)
          self.customContextMenuRequested.connect(self.show_context_menu)

          if self.viewMode() == 1:
               self.setIconSize(QSize(100,100))
               self.setStyleSheet("""
                    QListView::item{
                         margin: 10px 5px;
                         max-width: 150px;
                         min-width: 150px;
                         max-height: 150px;
                         height: 150px;
                         padding: 3px;
                         border-radius: 20px;
                    }
               """)

          self.setAcceptDrops(True)
          self.setDragEnabled(True)
          self.setDropIndicatorShown(True)
          self.setDragDropMode(QAbstractItemView.DragDrop)

          self.doubleClicked.connect(self.selectedToOpenDir)

     def copyMovePathMethod(self, type_):
          destination = self.filedialog.file.fileModel.rootPath()
          files = self.getSelectedItems()

          if type_ == "copy":
               results = file_api.copy_items(files, destination)
               self._show_operation_results("Copy", results)
          else:
               results = file_api.move_items(files, destination)
               self._show_operation_results("Move", results)
          self.filedialog.closeWindow()

     def _show_operation_results(self, operation: str, results: dict):
          """Show results of file operations"""
          successful = [path for path, success in results.items() if success]
          failed = [path for path, success in results.items() if not success]

          if successful:
               msg_box = QMessageBox(QMessageBox.Information, f"{operation} Complete",
                                   f"Successfully {operation.lower()}ed {len(successful)} item(s)", QMessageBox.Ok, self)
               msg_box.setFont(QFont("", 14))
               msg_box.exec_()
          if failed:
               msg_box = QMessageBox(QMessageBox.Warning, f"{operation} Failed",
                                   f"Failed to {operation.lower()} {len(failed)} item(s):\n" + "\n".join(failed), QMessageBox.Ok, self)
               msg_box.setFont(QFont("", 14))
               msg_box.exec_()

          # Refresh the view
          self.fileModel.layoutChanged.emit()

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
               QMessageBox.warning(self, "Error", f"Could not open file: {file_path}\n{e}")

     def show_context_menu(self, pos: QPoint):
          ix = self.indexAt(pos)
          self.contextMenu = AddContextMenu(self)
          self.newFolder = QAction("New Folder",self)
          self.openInConsole = QAction("Open in Terminal", self)
          self.openInConsole.triggered.connect(self.openTerminal)
          self.pasteFile = QAction("Paste")
          self.pasteFile.triggered.connect(self.pasteAction)
          self.selectAllContents = QAction("Select All")
          self.propertiesAction = QAction("Properties")

          self.newFolder.setShortcut("Ctrl+Shift+N")
          self.selectAllContents.setShortcut("Ctrl+A")
          self.pasteFile.setShortcut("Ctrl+P")

          self.openFolderFile = AddContextMenu("Open")
          self.openFolderFile.setTitle("Open")

          # OPEN FOLDER FILE CONTENTS
          self.openCurrent = QAction("Open")
          self.openCurrent.triggered.connect(lambda: self.selectedToOpenDir(ix))
          self.openInNewWindow = QAction("Open New Window")
          self.openInNewWindow.triggered.connect(self.openInNewWindowFunction)
          self.openInNewTab = QAction("Open New Tab")
          self.openInNewTab.triggered.connect(lambda: self.openInNewTabMethod(ix))

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
          self.copytoFileFolder.triggered.connect(lambda: self.filedialog.execute("copy"))
          self.movetoFileFolder.triggered.connect(lambda: self.filedialog.execute("move"))

          # RENAME, CREATE A LINK, COMPRESS, MOVE TO TRASH
          self.renameFileFolders = QAction("Rename...", self)
          self.createLinkFileFolder = QAction("Create a Link", self)
          self.createLinkFileFolder.triggered.connect(self.createLinkFolderFile)
          self.compressFileFolder = QAction("Compress...", self)
          self.encFileFolder = QAction("Encrypt...", self)
          self.decFileFolder = QAction("Decrypt...", self)
          self.compressFileFolder.triggered.connect(self.compressFolder)
          self.deletePermanently = QAction("Delete Permanently", self)
          self.deletePermanently.triggered.connect(lambda: self.action_delete(ix))
          self.deletePermanently.setShortcut("Shift+Del")
          self.movetoTrash = QAction()

          # Check if we're currently in the trash directory
          trash_path = trash_api.get_trash_path()  # Get the trash path from the API
          if self.fileModel.rootPath() == os.path.join(trash_path, "files"):
               self.movetoTrash.setText("Delete from Trash")
          else:
               self.movetoTrash.setText("Move to Trash")

          self.renameFileFolders.triggered.connect(lambda: self.renameFileFolder(ix))
          self.newFolder.triggered.connect(self.openCreationDialog)

          # PROPERTIES
          self.properties = QAction("Properties")

          self.renameFileFolders.setShortcut("F2")
          self.cutFileFolder.setShortcut("Ctrl+X")
          self.copyFileFolder.setShortcut("Ctrl+C")
          self.copyFileFolder.triggered.connect(lambda: self.copyAction("copy"))
          self.cutFileFolder.triggered.connect(lambda: self.copyAction("cut"))
          self.compressFileFolder.setShortcut("Ctrl+Shift+M")
          self.properties.setShortcut("Alt+Return")


          if ix.column() == 0:
               self.contextMenu.addMenu(self.openFolderFile)
               self.contextMenu.addSeparator()
               self.contextMenu.addActions([self.cutFileFolder, self.copyFileFolder, self.movetoFileFolder, self.copytoFileFolder, self.movetoFileFolder])
               self.contextMenu.addSeparator()
               self.contextMenu.addActions([self.renameFileFolders, self.createLinkFileFolder, self.compressFileFolder, self.encFileFolder, self.decFileFolder, self.movetoTrash])
               if self.movetoTrash.text() == "Move to Trash":
                    self.contextMenu.addAction(self.deletePermanently)
               self.contextMenu.addSeparator()
               self.contextMenu.addAction(self.properties)
          else:
               self.contextMenu.addActions([self.newFolder, self.openInConsole])
               self.contextMenu.addSeparator()
               self.contextMenu.addActions([self.pasteFile, self.selectAllContents])
               self.contextMenu.addSeparator()
               self.contextMenu.addAction(self.propertiesAction)

          self.encFileFolder.triggered.connect(self.encrypt)
          self.decFileFolder.triggered.connect(self.decrypt)
          self.properties.triggered.connect(self.showProperties)

          self.action = self.contextMenu.exec_(self.viewport().mapToGlobal(pos))


          if not self.action:
               return
          
          if self.action.text() == "Delete from Trash":
               self.action_delete(ix=ix)
          elif self.action.text() == "Move to Trash":
               self.moveToTrashMethod()

     def selectedToOpenDir(self, index: QModelIndex):
          # Map proxy index to source index
          source_index = self.proxyModel.mapToSource(index)
          path = self.fileModel.filePath(source_index)
          path = Path(path)
          if path.is_dir():
               self.setDirectory(path)
          else:
               self._open_file(str(path))

     def setDirectory(self, path: str):
          """Set directory with navigation history tracking"""
          path_str = str(path)
          
          # Add to history if different from current
          if path_str != self.history[self.current_history_index]:
               # Remove any forward history
               self.history = self.history[:self.current_history_index + 1]
               self.history.append(path_str)
               self.current_history_index = len(self.history) - 1
          
          # Update the model
          self.location_path = path_str
          self.fileModel.setRootPath(path_str)
          self.setRootIndex(self.proxyModel.mapFromSource(self.fileModel.index(path_str)))
          
          # Clear any active search
          self.proxyModel.setFilterFixedString("")
          
          # Update parent title bar path
          if hasattr(self.parent, 'title_bar'):
               self.parent.title_bar.update_path(path_str)

     def canGoBack(self):
          """Check if we can navigate back"""
          return self.current_history_index > 0

     def canGoForward(self):
          """Check if we can navigate forward"""
          return self.current_history_index < len(self.history) - 1

     def goBack(self):
          """Navigate to previous directory"""
          if self.canGoBack():
               self.current_history_index -= 1
               path = self.history[self.current_history_index]
               self.location_path = path
               self.fileModel.setRootPath(path)
               self.setRootIndex(self.proxyModel.mapFromSource(self.fileModel.index(path)))
               
               # Clear any active search
               self.proxyModel.setFilterFixedString("")
               
               # Update parent title bar path
               if hasattr(self.parent, 'title_bar'):
                    self.parent.title_bar.update_path(path)

     def goForward(self):
          """Navigate to next directory"""
          if self.canGoForward():
               self.current_history_index += 1
               path = self.history[self.current_history_index]
               self.location_path = path
               self.fileModel.setRootPath(path)
               self.setRootIndex(self.proxyModel.mapFromSource(self.fileModel.index(path)))
               
               # Clear any active search
               self.proxyModel.setFilterFixedString("")
               
               # Update parent title bar path
               if hasattr(self.parent, 'title_bar'):
                    self.parent.title_bar.update_path(path)

     def performSearch(self, text: str):
          """Filter files based on search text"""
          self.proxyModel.setFilterFixedString(text)
          # Update the root index to show filtered results
          if text:
               self.setRootIndex(self.proxyModel.mapFromSource(self.fileModel.index(self.location_path)))
          else:
               self.setRootIndex(self.proxyModel.mapFromSource(self.fileModel.index(self.location_path)))

     def encrypt(self):
          """Encrypt selected files"""
          selected_items = self.getSelectedItems()
          if selected_items:
               password, ok = QInputDialog.getText(self, "Encryption", "Enter password:", QLineEdit.Password)
               if ok and password:
                    results = encryption_api.encrypt_files(selected_items, password)
                    self._show_operation_results("Encrypt", results)

     def decrypt(self):
          """Decrypt selected files"""
          selected_items = self.getSelectedItems()
          if selected_items:
               password, ok = QInputDialog.getText(self, "Decryption", "Enter password:", QLineEdit.Password)
               if ok and password:
                    results = encryption_api.decrypt_files(selected_items, password)
                    self._show_operation_results("Decrypt", results)

     def openInNewTabMethod(self, index):
          # Map proxy index to source index
          source_index = self.proxyModel.mapToSource(index)
          path = self.fileModel.filePath(source_index)
          path = Path(path)
          if path.is_dir():
               self.parent.openNewTab2(str(path))

     def compressFolder(self):
          selected_items = self.getSelectedItems()
          if selected_items:
               archive_name = os.path.basename(selected_items[0])
               success = file_api.compress_items(selected_items, self.fileModel.rootPath(), archive_name)
               if success:
                    QMessageBox.information(self, "Compression Complete", "Files compressed successfully")
                    self.fileModel.layoutChanged.emit()
               else:
                    QMessageBox.warning(self, "Compression Failed", "Failed to compress files")

     def createLinkFolderFile(self):
          selected_items = self.getSelectedItems()
          results = {}
          for file in selected_items:
               results[file] = self.createLink(file=file)
          self._show_operation_results("Create Link", results)

     def createLink(self, file):
          """Create a link/shortcut to the file"""
          try:
               link_name = f"Link to {os.path.basename(file)}"
               link_path = os.path.join(self.fileModel.rootPath(), link_name)

               # Make sure we don't overwrite existing files
               counter = 1
               while os.path.exists(link_path):
                    name, ext = os.path.splitext(link_name)
                    link_path = os.path.join(self.fileModel.rootPath(), f"{name} ({counter}){ext}")
                    counter += 1

               if sys.platform == "win32":
                    # On Windows, create a shortcut (.lnk file)
                    self._create_windows_shortcut(file, link_path)
               else:
                    # On Unix-like systems, try to create symlink
                    try:
                         os.symlink(file, link_path)
                    except OSError:
                         # If symlink fails, create a copy
                         shutil.copy2(file, link_path)

               return True
          except Exception as e:
               print(f"Error creating link for {file}: {e}")
               return False

     def _create_windows_shortcut(self, target_path, shortcut_path):
          """Create a Windows shortcut (.lnk file)"""
          try:
               import winshell
               winshell.shortcut(target_path, shortcut_path)
          except ImportError:
               # If winshell is not available, create a simple text file with the path
               shortcut_path = shortcut_path.replace('.lnk', '.txt')
               with open(shortcut_path, 'w') as f:
                    f.write(f"Shortcut to: {target_path}\n")
          except Exception as e:
               # Fallback: create a copy
               shutil.copy2(target_path, shortcut_path)

     def openCreationDialog(self):
          self.creationFolderDialog = Creation(self)
          self.creationFolderDialog.exec_()

     def setDirectory(self, path: Path):
          self.fileModel.setRootPath(str(path))
          self.setRootIndex(self.proxyModel.mapFromSource(self.fileModel.index(self.fileModel.rootPath())))
          tabText = os.path.basename(self.fileModel.rootPath())
          if len(tabText) > 15:
               tabText = tabText[:40] + "..."
          self.parent.tab.setTabText(self.parent.tab.currentIndex(), tabText)
          self.parent.setInputPath()

     def getWorkingDirectory(self):
          pwd = self.fileModel.rootPath()
          return pwd

     def createFolder(self, folderName: str):
          if folderName != "":
               success = file_api.create_directory(self.fileModel.rootPath(), folderName)
               if success:
                    self.fileModel.layoutChanged.emit()
                    self.creationFolderDialog.closeDialog()
               else:
                    QMessageBox.warning(self, "Error", f"Could not create folder '{folderName}'")
          else:
               pass

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
               "Permanently Delete", f"Are you sure you want to permanently delete {file_name}?\nThis action cannot be undone."
          )
          if dialog == QMessageBox.Yes:
               selected_items = self.getSelectedItems()
               results = file_api.delete_items(selected_items, permanent=True)
               self._show_operation_results("Delete", results)

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
               # Map proxy index to source index
               source_index = self.proxyModel.mapToSource(index)
               file_info = self.fileModel.fileInfo(source_index)
               selected_items.append(file_info.absoluteFilePath())
          return selected_items
     
     def moveToTrashMethod(self):
          selected_items = self.getSelectedItems()
          results = {}
          for item in selected_items:
               results[item] = trash_api.move_to_trash(item)
          self._show_operation_results("Move to Trash", results)

     def openInNewWindowFunction(self):
          selectdItems = self.getSelectedItems()
          for item in selectdItems:
               abspath = os.path.abspath(item)
               self.parent.openFolderInNewWindow(abspath)

     def copyAction(self, type_):
          selectedItems = self.getSelectedItems()
          item_list = f"{type_}\n"
          for i in selectedItems:
               item_list += i+"\n"
          QApplication.clipboard().setText(item_list)

     def pasteAction(self):
          files = QApplication.clipboard().text().split("\n")
          if files[0] == "copy":
               for file in files:
                    file = Path(file)
                    if file.exists():
                         if file.is_dir():
                              try:
                                   shutil.copytree(str(file), f"{self.fileModel.rootPath()}/{str(os.path.basename(file))}")
                              except:
                                   pass
                         else:
                              try:
                                   shutil.copy(str(file), f"{self.fileModel.rootPath()}/")
                              except:
                                   pass
               self.show_dialog("Coped", "Files Copied Successfully")
          else:
               for file in files:
                    file = Path(file)
                    if file.exists():
                         if file.is_dir():
                              try:
                                   shutil.move(str(file), f"{self.fileModel.rootPath()}/{str(os.path.basename(file))}")
                              except:
                                   pass
                         else:
                              try:
                                   shutil.move(str(file), f"{self.fileModel.rootPath()}/")
                              except:
                                   pass
               self.show_dialog("Coped", "Files Copied Successfully")

     def openTerminal(self):
          if sys.platform == "linux":
               try:
                    subprocess.Popen(['gnome-terminal', '--working-directory', self.fileModel.rootPath()])
               except:
                    subprocess.Popen(['mate-terminal', '--working-directory', self.fileModel.rootPath()])
          else:
               try:
                    subprocess.Popen(['powershell.exe', '-NoExit', '-Command', f"cd {self.fileModel.rootPath()}"])
               except:  pass

     def encrypt(self):
          """Encrypt selected files"""
          selected_items = self.getSelectedItems()
          if selected_items:
               password, ok = QInputDialog.getText(self, "Encryption", "Enter password:", QLineEdit.Password)
               if ok and password:
                    results = encryption_api.encrypt_files(selected_items, password)
                    self._show_operation_results("Encrypt", results)

     def decrypt(self):
          """Decrypt selected files"""
          selected_items = self.getSelectedItems()
          if selected_items:
               password, ok = QInputDialog.getText(self, "Decryption", "Enter password:", QLineEdit.Password)
               if ok and password:
                    results = encryption_api.decrypt_files(selected_items, password)
                    self._show_operation_results("Decrypt", results)

     def showProperties(self):
          selected_items = self.getSelectedItems()
          if selected_items:
               item_path = selected_items[0]  # Show properties for first selected item
               info = file_api.get_item_info(item_path)
               if info:
                    self._show_item_properties(info)
               else:
                    QMessageBox.warning(self, "Error", "Could not get item information")

     def _show_item_properties(self, info: dict):
          """Show item properties dialog"""
          dialog = QDialog(self)
          dialog.setWindowTitle("Properties")
          dialog.setModal(True)

          layout = QVBoxLayout(dialog)

          # Item details
          form_layout = QFormLayout()

          form_layout.addRow("Name:", QLabel(info['name']))
          form_layout.addRow("Path:", QLabel(info['path']))
          form_layout.addRow("Type:", QLabel("Directory" if info['is_dir'] else "File"))
          form_layout.addRow("Size:", QLabel(f"{info['size']} bytes"))
          form_layout.addRow("Modified:", QLabel(time.ctime(info['modified'])))

          layout.addLayout(form_layout)

          # Close button
          close_btn = QPushButton("Close")
          close_btn.clicked.connect(dialog.accept)
          layout.addWidget(close_btn)

          dialog.exec_()

     # drag and drop functionality
     def dragEnterEvent(self, e: QDragEnterEvent) -> None:
          if e.mimeData().hasUrls():
               e.accept()
          else:
               e.ignore()

     def dropEvent(self, e: QDropEvent) -> None:
          root_path = Path(self.fileModel.rootPath())
          if e.mimeData().hasUrls():
               for url in e.mimeData().urls():
                    path = Path(url.toLocalFile())
                    if path.is_dir():
                         shutil.copytree(path, root_path / path.name)
                    else:
                         if root_path.samefile(self.fileModel.rootPath()):
                              idx: QModelIndex = self.indexAt(e.pos())
                              if idx.column() == -1:
                                   shutil.move(path, root_path / path.name)
                              else:
                                   folder_path = Path(self.fileModel.filePath(idx))
                                   shutil.move(path, folder_path / path.name)
                         else:
                              shutil.copy(path, root_path / path.name)
          e.accept()
          return super().dropEvent(e)

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

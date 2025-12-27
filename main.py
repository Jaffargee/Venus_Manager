from PyQt5 import QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys, os
from pathlib import Path
from PyQt5.QtWidgets import QWidget
from containers import *
from file_manager_ import *
from SideBar import *


class MainWindow(QMainWindow):
     def __init__(self, path=None):
          if path is None:
               if sys.platform == "win32":
                    path = f"C:/Users/{getpass.getuser()}/"
               else:
                    path = f"/home/{getpass.getuser()}/"
          self.path = path
          QMainWindow.__init__(self)
          self.radius = 10
          # self.setGeometry(50,50,1200,600)
          self.resize(QSize(1200, 600))
          self.setContentsMargins(0,0,0,0)
          self.setMinimumSize(400, 400)
          self.shadow = QGraphicsDropShadowEffect()
          self.shadow.setBlurRadius(10)
          self.shadow.setColor(QColor("#000"))
          self.shadow.setOffset(QPoint(10,10))
          self.setGraphicsEffect(self.shadow)
          self.setWindowTitle("Venus Manager")
          self.setWindowIcon(QIcon("folder-teal-desktop.svg"))
          
          if self.isMaximized(): pass
          else: self.showMaximized()

          self.stylesheet = open("./venus/venus_st.css")
          self.setStyleSheet(self.stylesheet.read())
          
          self.windowWidget = Window(self, path)

          self.titlebar = TitleBar(self, self.path)
          self.addToolBar(self.titlebar)

          self.setCentralWidget(self.windowWidget)

          self.titlebar.newWindow.triggered.connect(self.createNewWindow)
          self.titlebar.newTab.triggered.connect(self.windowWidget.openNewTab)
          self.titlebar.pathInputDirectory.returnPressed.connect(lambda: self.windowWidget.setDirectory(self.titlebar.pathInputDirectory.text()))

     def createNewWindow(self):
          window = MainWindow()
          window.show()


class Window(QWidget):
     def __init__(self, parent: MainWindow, path):
          super().__init__()
          self.parent = parent
          self.path = path
          self.setObjectName("mainWidget")
          self.windowLayout = QHBoxLayout(self)
          self.windowLayout.setAlignment(Qt.AlignLeft)
          self.windowLayout.setContentsMargins(0,0,0,0)
          self.windowLayout.setSpacing(0)

          self.tab = QTabWidget()
          self.tab.setObjectName("windowTab")
          self.tab.setMovable(True)
          self.tab.setMouseTracking(True)
          self.tab.setTabBarAutoHide(True)
          self.tab.setTabsClosable(True)

          self.sideBar = SideBar()

          self.bodyFileContent = FileManager(self, self.path)

          self.tab.addTab(self.bodyFileContent, os.path.basename(self.bodyFileContent.fileModel.rootPath()))

          self.sideBar.favorites.itemClicked.connect(self.selectedDir)

          self.windowLayout.addWidget(self.sideBar)
          self.windowLayout.addWidget(self.tab)

          self.tab.tabCloseRequested.connect(self.closeTab)

          self.isWraping = self.tab.currentWidget().viewMode()

     def openFolderInNewWindow(self, path):
          window = MainWindow(path=path)
          window.show()

     def openNewTab(self):
          self.bodyFileContent = FileManager(self, self.tab.currentWidget().fileModel.rootPath())
          tabText = os.path.basename(self.bodyFileContent.fileModel.rootPath())
          if len(tabText) > 15:
               tabText = tabText[:40] + "..."
          self.tab.addTab(self.bodyFileContent, tabText)
          self.setInputPath()
          self.tab.setCurrentIndex(self.tab.count() - 1)

     def openNewTab2(self, path):
          self.bodyFileContent = FileManager(self, path)
          tabText = os.path.basename(self.bodyFileContent.fileModel.rootPath())
          if len(tabText) > 15:
               tabText = tabText[:40] + "..."
          self.tab.addTab(self.bodyFileContent, tabText)
          self.setInputPath()
          self.tab.setCurrentIndex(self.tab.count() - 1)

     def listView(self):
          if self.isWraping == 0:
               self.isWraping = 2
               self.tab.currentWidget().setViewMode(QListView.ViewMode.IconMode)
               self.tab.currentWidget().setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
               self.tab.currentWidget().setAutoScroll(True)
               self.tab.currentWidget().setResizeMode(QListView.Adjust)
               self.tab.currentWidget().setWordWrap(True)
               self.tab.currentWidget().setWrapping(True)
               self.tab.currentWidget().setIconSize(QSize(100,100))
               self.tab.currentWidget().setStyleSheet("""
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
          elif self.isWraping == 1:
               self.isWraping = 0
               self.tab.currentWidget().setViewMode(QListView.ViewMode.ListMode)
               self.tab.currentWidget().setIconSize(QSize(30,30))
               self.tab.currentWidget().setWrapping(False)
               self.tab.currentWidget().setStyleSheet("""
                         QListView::item{
                              padding: 6px 10px;
                              border: 2px solid transparent;
                              border-radius: 6px;
                              margin: 2px;
                         }
                    """)
          else:
               self.isWraping = 1
               self.tab.currentWidget().setViewMode(QListView.ViewMode.ListMode)
               self.tab.currentWidget().setIconSize(QSize(30,30))
               self.tab.currentWidget().setWrapping(True)
               self.tab.currentWidget().setStyleSheet("""
                         QListView::item{
                              padding: 6px 10px;
                              border: 2px solid transparent;
                              border-radius: 6px;
                              margin: 2px;
                         }
                    """)

     def selectedDir(self, item):
          item_text = item.text()
          if item_text == "Other Locations":
               self.tab.currentWidget().setDirectory(Path("/" if sys.platform == "linux" else "C:/"))
          else:
               # Find the shortcut with matching title
               for shortcut in self.sideBar.favorites.shortcuts:
                    if shortcut["title"] == item_text:
                         self.tab.currentWidget().setDirectory(Path(shortcut["path"]))
                         self.setInputPath()
                         break

     def setDirectory(self, path):
          self.tab.currentWidget().setDirectory(Path(path))

     def setInputPath(self):
          self.parent.titlebar.pathInputDirectory.setText(self.tab.currentWidget().getWorkingDirectory())

     def closeTab(self, i):
          # if there is only one tab
          if self.tab.count() < 2:
               # do nothing
               return

          # else remove the tab
          self.tab.removeTab(i)

def Main():
     app = QApplication(sys.argv)
     app.styleHints().setShowShortcutsInContextMenus(True)
     clipboard = app.clipboard()
     Window = MainWindow()
     Window.show()
     sys.exit(app.exec_())
        
        
if __name__ == "__main__":
     Main()
          
          
          
          

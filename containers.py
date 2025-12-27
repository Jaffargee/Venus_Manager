from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import os
from pathlib import Path
import getpass
import sys
from menu import AddContextMenu
from file_manager_ import FileManager
from gui_download import Window
import subprocess

class StatusBar(QStatusBar):
     def __init__(self, parent):
          super(StatusBar, self).__init__()
          self.parent = parent

class TitleBar(QToolBar):
     def __init__(self, parent: QMainWindow, path=None):
          super(TitleBar, self).__init__()
          self.parent = parent
          self.setMovable(False)
          self.setContentsMargins(0,0,0,0)

          self.shadow = QGraphicsDropShadowEffect()
          self.shadow.setBlurRadius(2.0)
          self.shadow.setOffset(QPoint(6, 0))
          self.shadow.setColor(QColor("#000"))

          self.setGraphicsEffect(self.shadow)

          # Locator Frame Layout
          self.locatorFrame = QFrame()
          self.locatorFrame.setContentsMargins(0,0,0,0)
          self.locatorFrameLayout = QHBoxLayout(self.locatorFrame)
          self.locatorFrameLayout.setContentsMargins(7,0,7,0)

          self.fileManager = FileManager(self, path=path)

          self.__initUi()
          self.updateNavigationButtons()
          # Adding widget to the toolbar
          self.addWidget(self.locatorFrame)



     def __initUi(self):
          self.LocatorPanel()

     def LocatorPanel(self):
          # LEFT CONTENTS FRAME AND LAYOUT
          self.leftContents = QFrame()
          self.leftContents.setMaximumWidth(300)
          self.leftContents.setObjectName("leftContents")
          self.leftContentsLayout = QHBoxLayout(self.leftContents)
          self.leftContents.setContentsMargins(0,0,0,0)
          self.leftContentsLayout.setContentsMargins(0,0,0,0)
          self.leftContentsLayout.setAlignment(Qt.AlignLeft)

          # RIGHT CONTENTS FRAME AND LAYOUT
          self.rightContents = QFrame()
          self.rightContents.setMaximumWidth(370)
          self.rightContents.setObjectName("rightContents")
          self.rightContentsLayout = QHBoxLayout(self.rightContents)
          self.rightContents.setContentsMargins(0,0,0,0)
          self.rightContentsLayout.setContentsMargins(0,0,0,0)
          self.rightContentsLayout.setAlignment(Qt.AlignRight)

          # CENTER CONTENTS AND LYAOUT
          self.centerContents = QFrame()
          self.centerContents.setObjectName("centerContents")
          self.centerContentsLayout = QHBoxLayout(self.centerContents)
          self.centerContents.setContentsMargins(0,0,0,0)
          self.centerContentsLayout.setContentsMargins(0,0,0,0)

          # DIR BUTTONS FOR CENTER CONTENTS AND THEIR LAYOUT
          self.dirButtonContainer = QFrame()
          self.dirButtonContainer.setObjectName("dirButtonContainer")
          self.dirButtonContainerLayout = QHBoxLayout(self.dirButtonContainer)
          self.dirButtonContainerLayout.setAlignment(Qt.AlignLeft)
          self.dirButtonContainer.setContentsMargins(0,0,0,0)
          self.dirButtonContainerLayout.setContentsMargins(0,0,0,0)


          # NAVIGATION BUTTONS BACKWARD AND FORWARD BUTTON
          self.backwardButton = QPushButton()
          self.forwardButton = QPushButton()

          # SETTING ICON TO NAVIGATION BUTTON
          self.backwardButton.setIcon(QIcon("./icons/arrow-left.svg"))
          self.forwardButton.setIcon(QIcon("./icons/arrow-right.svg"))

          # SETTING OBJECT NAME FOR NAVIGATION BUTTONS
          self.backwardButton.setObjectName("toolBarButton")
          self.forwardButton.setObjectName("toolBarButton")

          # Connect navigation buttons
          self.backwardButton.clicked.connect(self.goBack)
          self.forwardButton.clicked.connect(self.goForward)


          # DIR BUTTONS AND LAYOUT INSIDE CONTAINER
          path = str(self.fileManager.fileModel.rootPath())
          self.pathInputDirectory = QLineEdit(path)
          self.pathInputDirectory.setObjectName("pathInputDirectory")
          

          # FILE OPERATION BUTTON INSIDE THE CENTER CONTENTS CONTAINER
          self.operationButton = QPushButton()
          self.operationButton.setObjectName("operationButton")
          self.operationButton.setIcon(QIcon("./icons/more.svg"))

          ########################################################
          ########################################################

          self.operationButtonMenu = AddContextMenu(self)
          self.openInConsole = QAction("Open In Terminal")
          self.reloadDir = QAction("Reload")
          self.reloadDir.setShortcut("F5")
          self.copyLocation = QAction("Copy Location")
          self.copyLocation.triggered.connect(lambda: QApplication.clipboard().setText(self.pathInputDirectory.text()))
          self.properties = QAction("Properties")

          # Events
          self.openInConsole.triggered.connect(self.openTerminal)
          self.copyLocation.triggered.connect(self.copyLocationPath)
          self.reloadDir.triggered.connect(self.reloadDirFunction)

          self.operationButtonMenu.addActions([self.openInConsole])
          self.operationButtonMenu.addSeparator()
          self.operationButtonMenu.addActions([self.reloadDir, self.copyLocation])
          self.operationButtonMenu.addSeparator()
          self.operationButtonMenu.addAction(self.properties)

          self.operationButton.setMenu(self.operationButtonMenu)

          ########################################################
          ########################################################

          # VIEW AND SORT BUTTONS CONTAINER
          self.viewSortContainer = QFrame()
          self.viewSortContainer.setObjectName("viewSortContainer")
          self.viewSortContainerLayout = QHBoxLayout(self.viewSortContainer)
          self.viewSortContainer.setContentsMargins(0,0,0,0)
          self.viewSortContainerLayout.setContentsMargins(0,0,0,0)
          self.viewSortContainerLayout.setSpacing(0)

          # Search Button
          self.searchButton = QPushButton()
          self.searchButton.setObjectName("toolBarButton")
          self.searchButton.setIcon(QIcon("./icons/search.svg"))
          self.searchButton.clicked.connect(self.searchInputDisplay)

          # Search Button
          self.downloadButton = QPushButton()
          self.downloadButton.setObjectName("toolBarButton")
          self.downloadButton.setIcon(QIcon("./icons/download-2.svg"))
          self.downloadButton.clicked.connect(self.main)

          # View Button
          self.viewButton = QPushButton()
          self.viewButton.setObjectName("toolBarButton")
          self.viewButton.setIcon(QIcon("./icons/list.svg"))
          self.viewButton.clicked.connect(self.parent.windowWidget.listView)

          # Menu Button
          self.menuButton = QPushButton()
          self.menuButton.setObjectName("toolBarButton")
          self.menuButton.setIcon(QIcon("./icons/menu.svg"))

          # Menu Button Declaration
          self.locatorMenu = AddContextMenu(self, 230)

          self.newWindow = QAction("New Window")
          self.newTab = QAction("New Tab")

          self.newWindow.setShortcut("Ctrl+N")
          self.newTab.setShortcut("Ctrl+T")

          self.zoomSection = QWidgetAction(self)
          self.widgetFrame = QFrame()
          self.widgetFrameLayout = QHBoxLayout(self.widgetFrame)
          # self.widgetFrame.setContentsMargins(0,0,0,0)
          self.widgetFrameLayout.setContentsMargins(0,0,0,0)

          self.iconSizeLabel = QLabel("Icon Size")
          self.addSizeButton = QPushButton()
          self.reduceSizeButton = QPushButton()
          self.addSizeButton.setIcon(QIcon("./icons/zoom-in.svg"))
          self.reduceSizeButton.setIcon(QIcon("./icons/zoom-out.svg"))

          self.addSizeButton.setIconSize(QSize(23,23))
          self.reduceSizeButton.setIconSize(QSize(23,23))

          self.iconSizeLabel.setObjectName("menuLabel")
          self.addSizeButton.setObjectName("toolBarButton")
          self.reduceSizeButton.setObjectName("toolBarButton")

          self.widgetFrameLayout.addWidget(self.iconSizeLabel, alignment=Qt.AlignLeft)
          self.widgetFrameLayout.addStretch()
          self.widgetFrameLayout.addWidget(self.addSizeButton, alignment=Qt.AlignRight)
          self.widgetFrameLayout.addWidget(self.reduceSizeButton, alignment=Qt.AlignRight)

          self.zoomSection.setDefaultWidget(self.widgetFrame)

          # ADDING QACTION TO THE MENU BUTTON 
          self.locatorMenu.addAction(self.newWindow)
          self.locatorMenu.addAction(self.newTab)
          self.locatorMenu.addSection("Zoom Section")
          self.locatorMenu.addAction(self.zoomSection)
          self.menuButton.setMenu(self.locatorMenu)

          # ICON SIZE
          self.backwardButton.setIconSize(QSize(20,20))
          self.forwardButton.setIconSize(QSize(20, 20))
          self.menuButton.setIconSize(QSize(20,20))
          self.operationButton.setIconSize(QSize(20,20))
          self.searchButton.setIconSize(QSize(20,20))

          # ADDING VIEW AND SORT BUTTON THE VIEW-SORT CONTAINER LAYOUT
          self.viewSortContainerLayout.addWidget(self.viewButton)

          # ADDING BACKWARD AND FORWARD BUTTON TO THE LEFT CONTENT LAYOUT
          self.leftContentsLayout.addWidget(self.backwardButton)
          self.leftContentsLayout.addWidget(self.forwardButton)

          # ADDING RIGHT CONTENT BUTTONS LAYOUT TO THE RIGHT CONTENT LAYOUT
          self.rightContentsLayout.addWidget(self.searchButton)
          self.rightContentsLayout.addWidget(self.viewSortContainer)
          self.rightContentsLayout.addWidget(self.downloadButton)
          self.rightContentsLayout.addWidget(self.menuButton)
          # self.rightContentsLayout.addWidget(self.closeButton)
          
          # ADDING DIR BUTTON CONTAINER AND OPERATION BUTTON TO THE CENTER CONTENT CONTAINER LAYOUT
          self.centerContentsLayout.addWidget(self.pathInputDirectory)
          self.centerContentsLayout.addWidget(self.operationButton, alignment=Qt.AlignRight)

          # ADDING LEFT CONTENT, CENTER CONTENT AND THE RIGHT CONTENT CONTAINERS TO THE MAIN LOCATOR FRAME LAYOUT
          self.locatorFrameLayout.addWidget(self.leftContents)
          self.locatorFrameLayout.addWidget(self.centerContents)
          self.locatorFrameLayout.addWidget(self.rightContents)

          self.searchContainer = QFrame()
          self.searchContainerLayout = QHBoxLayout(self.searchContainer)
          self.searchContainer.setContentsMargins(0,0,0,0)
          self.searchContainerLayout.setContentsMargins(0,0,0,0)
          self.searchContainerLayout.setSpacing(0)
          self.searchContainer.setObjectName("searchContainer")
          self.searchContainer.setHidden(True)

          self.searchInput = QLineEdit()
          self.searchInput.setObjectName("searchInput")
          self.searchInput.setPlaceholderText("Search")
          self.searchInput.setClearButtonEnabled(True)
          # self.searchInput.addAction(QIcon("./icons/search-dark.svg"), QLineEdit.ActionPosition.LeadingPosition)
          self.searchInput.findChildren(QAction)[0].setIcon(QIcon("./icons/cancel.svg"))
          self.searchInput.textChanged.connect(self.performSearch)

          self.searchIcon = QPushButton()
          self.searchIcon.setIcon(QIcon("./icons/search-dark.svg"))
          self.searchIcon.setIconSize(QSize(22,22))
          self.searchIcon.setEnabled(False)
          self.searchIcon.setObjectName("operationButton")

          self.searchContainerLayout.addWidget(self.searchIcon)
          self.searchContainerLayout.addWidget(self.searchInput)

          self.searchContainer.mousePressEvent = self.mousePressEvent
          self.searchContainer.mouseReleaseEvent = self.mouseReleaseEvent

     def main(self):
          try:
               window = Window(self.parent.windowWidget.tab.currentWidget().fileModel.rootPath())
               self.parent.windowWidget.tab.addTab(window, "Downloads")
               self.parent.windowWidget.tab.setCurrentWidget(window)
          except: pass

     def openTerminal(self):
          if sys.platform == "linux":
               try:
                    subprocess.Popen(['gnome-terminal', '--working-directory', self.pathInputDirectory.text()])
               except:
                    subprocess.Popen(['mate-terminal', '--working-directory', self.pathInputDirectory.text()])
          else:
               try:
                    subprocess.Popen(['powershell.exe', '-NoExit', '-Command', f"cd {self.pathInputDirectory.text()}"])
               except:  pass

     def copyLocationPath(self):
          QApplication.clipboard().setText(self.pathInputDirectory.text())

     def reloadDirFunction(self):
          self.path = self.pathInputDirectory.text()
          self.reloadPath("/")
          self.reloadPath(self.path)

     def reloadPath(self, path):
          self.parent.windowWidget.setDirectory(path)

     def goBack(self):
          """Navigate back in history"""
          if self.fileManager.canGoBack():
               self.fileManager.goBack()
               self.updateNavigationButtons()

     def goForward(self):
          """Navigate forward in history"""
          if self.fileManager.canGoForward():
               self.fileManager.goForward()
               self.updateNavigationButtons()

     def updateNavigationButtons(self):
          """Update the enabled state of navigation buttons"""
          self.backwardButton.setEnabled(self.fileManager.canGoBack())
          self.forwardButton.setEnabled(self.fileManager.canGoForward())

     def update_path(self, path: str):
          """Update the path display in the title bar"""
          self.pathInputDirectory.setText(path)
          self.updateNavigationButtons()

     def performSearch(self, text: str):
          """Perform search filtering on the file manager"""
          self.fileManager.performSearch(text)

     def searchInputDisplay(self):
          """Toggle search input visibility"""
          if self.searchContainer.isHidden():
               self.searchContainer.setHidden(False)
               self.searchInput.setFocus()
          else:
               self.searchContainer.setHidden(True)
               self.searchInput.clear()
               self.fileManager.performSearch("")  # Clear search

     def mouseDoubleClickEvent(self, a0: QMouseEvent) -> None:
          if self.parent.isMaximized():
               self.parent.showNormal()
          else:
               self.parent.showMaximized()

     def quitWindow(self):
          self.parent.close()

     def searchInputDisplay(self):
          if self.centerContents.isHidden():
               self.locatorFrameLayout.replaceWidget(self.searchContainer, self.centerContents)
               self.centerContents.setHidden(False)
               self.searchContainer.setHidden(True)
          else:
               self.locatorFrameLayout.replaceWidget(self.centerContents, self.searchContainer)
               self.centerContents.setHidden(True)
               self.searchContainer.setHidden(False)
               self.searchInput.setFocus()
               if self.searchContainer.hasFocus(): print("Hello world")
     





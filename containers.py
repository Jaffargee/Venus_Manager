from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import os
from pathlib import Path
import getpass
import sys
from menu import AddContextMenu
from file_manager_ import FileManager

class StatusBar(QStatusBar):
     def __init__(self, parent):
          super(StatusBar, self).__init__()
          self.parent = parent

class TitleBar(QToolBar):
     def __init__(self, parent: QMainWindow):
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

          # Adding widget to the toolbar
          self.addWidget(self.locatorFrame)

          self.fileManager = FileManager(self)

          self.__initUi()

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



#####################################################################################
#####################################################################################
#####################################################################################
#####################################################################################





          # DIR BUTTONS AND LAYOUT INSIDE CONTAINER
          path = str(self.fileManager.fileModel.rootPath()).split("/")
          self.dirButton1 = QPushButton(f"{path[1]}")
          self.dirButton1.setIcon(QIcon("./icons/home.svg"))
          self.dirButton1.setIconSize(QSize(20,20))
          self.dirSeperatorLabel1 = QLabel(">")
          self.dirButtonContainerLayout.addWidget(self.dirButton1)
          self.dirButtonContainerLayout.addWidget(self.dirSeperatorLabel1)
          for i in path[2: -1]:
               self.dirButton2 = QPushButton(f"{i}")
               self.dirSeperatorLabel2 = QLabel(">")
               self.dirButtonContainerLayout.addWidget(self.dirButton2)
               self.dirButtonContainerLayout.addWidget(self.dirSeperatorLabel2)
          self.dirButton3 = QPushButton(f"{path[-1]}")
          self.dirButton3.setDisabled(True)
          self.dirButton3.setStyleSheet("color: #fff;")
          self.dirButtonContainerLayout.addWidget(self.dirButton3)
          self.setLocatorDir(path=path)



#####################################################################################
#####################################################################################
#####################################################################################
#####################################################################################







          # FILE OPERATION BUTTON INSIDE THE CENTER CONTENTS CONTAINER
          self.operationButtons = QPushButton()
          self.operationButtons.setObjectName("operationButton")
          self.operationButtons.setIcon(QIcon("./icons/more.svg"))

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

          # View Button
          self.viewButton = QPushButton()
          self.viewButton.clicked.connect(lambda: print("GeeksforGeeks"))
          self.viewButton.setObjectName("viewButton")
          self.viewButton.setIcon(QIcon("./icons/list.svg"))

          # Sort Button
          self.sortButton = QPushButton()
          self.sortButton.setMaximumWidth(17)
          self.sortButton.clicked.connect(lambda: print("GeeksforGeeks nine nine"))
          self.sortButton.setObjectName("sortButton")
          self.sortButton.setIcon(QIcon("./icons/arrow-down-fill.svg"))

          # Menu Button
          self.menuButton = QPushButton()
          self.menuButton.setObjectName("toolBarButton")
          self.menuButton.setIcon(QIcon("./icons/menu.svg"))

          # CLOSE WINDOW BUTTON
          # self.closeButton = QPushButton()
          # self.closeButton.clicked.connect(self.quitWindow)
          # self.closeButton.setObjectName("closeWindowButton")
          # self.closeButton.setIcon(QIcon("./icons/cancel.svg"))

          # Menu Button Declaration
          self.locatorMenu = AddContextMenu(self, 230)

          self.newWindow = QAction("New Window")
          self.newTab = QAction("New Window")

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
          self.operationButtons.setIconSize(QSize(20,20))
          self.searchButton.setIconSize(QSize(20,20))
          # self.closeButton.setIconSize(QSize(13,13))

          # ADDING VIEW AND SORT BUTTON THE VIEW-SORT CONTAINER LAYOUT
          self.viewSortContainerLayout.addWidget(self.viewButton)
          self.viewSortContainerLayout.addWidget(self.sortButton)

          # ADDING BACKWARD AND FORWARD BUTTON TO THE LEFT CONTENT LAYOUT
          self.leftContentsLayout.addWidget(self.backwardButton)
          self.leftContentsLayout.addWidget(self.forwardButton)

          # ADDING RIGHT CONTENT BUTTONS LAYOUT TO THE RIGHT CONTENT LAYOUT
          self.rightContentsLayout.addWidget(self.searchButton)
          self.rightContentsLayout.addWidget(self.viewSortContainer)
          self.rightContentsLayout.addWidget(self.menuButton)
          # self.rightContentsLayout.addWidget(self.closeButton)
          
          # ADDING DIR BUTTON CONTAINER AND OPERATION BUTTON TO THE CENTER CONTENT CONTAINER LAYOUT
          self.centerContentsLayout.addWidget(self.dirButtonContainer, alignment=Qt.AlignLeft)
          self.centerContentsLayout.addStretch()
          self.centerContentsLayout.addWidget(self.operationButtons, alignment=Qt.AlignRight)

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

          self.searchIcon = QPushButton()
          self.searchIcon.setIcon(QIcon("./icons/search-dark.svg"))
          self.searchIcon.setIconSize(QSize(22,22))
          self.searchIcon.setEnabled(False)
          self.searchIcon.setObjectName("operationButton")

          self.searchContainerLayout.addWidget(self.searchIcon)
          self.searchContainerLayout.addWidget(self.searchInput)

          self.searchContainer.mousePressEvent = self.mousePressEvent
          self.searchContainer.mouseReleaseEvent = self.mouseReleaseEvent

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

     def setLocatorDir(self, path):
          path = path
          self.dirButton1.setText(path[1])
          for i in path[2:-1]:
               self.dirButton2.setText(i)
          self.dirButton3.setText(path[-1])
          
class SideBar(QFrame):
     def __init__(self) -> None:
          super().__init__()
          self.setContentsMargins(0,0,0,0)
          self.setFixedWidth(240)
          self.setObjectName("sidebar")
          """
               WE HAVE TWO FRAMES
               1. FAVORITES DIRECTORIES
               2. BOOKMARKS
               - FAVORITES DIRECTORIES
                    * DESKTOP
                    * DOWNLOADS
                    * DOCUMENTS
                    * MUSIC
                    * VIDEOS
                    * PICTURES
                    IF LINUX ? HOME : PC-USERNAME -> WINDOWS
                    TRASH
          """

          self.listLayout = QVBoxLayout(self)
          self.listLayout.setContentsMargins(0,0,0,0)
          self.listLayout.setSpacing(0)
          self.listLayout.setAlignment(Qt.AlignTop)

          self.favorites = ShortCuts()
          self.listLayout.addWidget(self.favorites)

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

class ShortCuts(QListWidget):
     def __init__(self):
          super(ShortCuts, self).__init__()
          self.setAcceptDrops(True)  # enable drag and drop functionality

          delegate = CategoryLabelDelegate(self)
          self.setItemDelegate(delegate)

          self.setIconSize(QSize(25,25))
        
          self.favLinux = [
               {"icon": QIcon("./icons/home.svg"), "title": "Home", "Home": {"path": f"/home/{getpass.getuser()}/"}},
               {"icon": QIcon("./icons/desktop.svg"), "title": "Desktop", "Desktop": {"path": f"/home/{getpass.getuser()}/Desktop"}},
               {"icon": QIcon("./icons/file.svg"), "title": "Documents", "Documents": {"path": f"/home/{getpass.getuser()}/Documents"}},
               {"icon": QIcon("./icons/download.svg"), "title": "Downloads", "Downloads": {"path": f"/home/{getpass.getuser()}/Downloads"}},
               {"icon": QIcon("./icons/music.svg"), "title": "Music", "Music": {"path": f"/home/{getpass.getuser()}/Music"}},
               {"icon": QIcon("./icons/gallery.svg"), "title": "Pictures", "Pictures": {"path": f"/home/{getpass.getuser()}/Pictures"}},
               {"icon": QIcon("./icons/video.svg"), "title": "Videos", "Videos": {"path": f"/home/{getpass.getuser()}/Videos"}},
               {"icon": QIcon("./icons/trash.svg"), "title": "Trash", "Trash": {"path": f"/home/{getpass.getuser()}/.Trash"}},
          ]
          self.favWindows = [
               {"icon": QIcon("./icons/home.svg"), "title": "Home", "Home": {"path": f"C:/{getpass.getuser()}/"}},
               {"icon": QIcon("./icons/desktop.svg"), "title": "Desktop", "Desktop": {"path": f"C:/{getpass.getuser()}/Desktop"}},
               {"icon": QIcon("./icons/file.svg"), "title": "Documents", "Documents": {"path": f"C:/{getpass.getuser()}/Documents"}},
               {"icon": QIcon("./icons/download.svg"), "title": "Downloads", "Downloads": {"path": f"C:/{getpass.getuser()}/Downloads"}},
               {"icon": QIcon("./icons/music.svg"), "title": "Music", "Music": {"path": f"C:/{getpass.getuser()}/Music"}},
               {"icon": QIcon("./icons/gallery.svg"), "title": "Pictures", "Pictures": {"path": f"C:/{getpass.getuser()}/Pictures"}},
               {"icon": QIcon("./icons/video.svg"), "title": "Videos", "Videos": {"path": f"C:/{getpass.getuser()}/Videos"}},
               {"icon": QIcon("./icons/trash.svg"), "title": "Trash", "Trash": {"path": f"C:/{getpass.getuser()}/.Trash"}},
          ]


          self.bookmarks = {
               "Tutorials": QIcon("./icons/folder.svg"),
               "Coding": QIcon("./icons/folder.svg"),
               "Setups": QIcon("./icons/folder.svg")
          }

          self.devices = {
               "Other Locations": QIcon("./icons/plus.svg")
          }

          if sys.platform == "linux":
               for fav in self.favLinux:
                    self.addFavoriteDirectory(dirname=fav["title"], icon=fav["icon"], listwidget=self)
          elif sys.platform == "win32":
               for fav in self.favWindows:
                    self.addFavoriteDirectory(dirname=fav["title"], icon=fav["icon"], listwidget=self)

          for dirname, icon in self.devices.items():
               self.addFavoriteDirectory(dirname=dirname, icon=icon, listwidget=self)


     def addFavoriteDirectory(self, dirname: str, icon: QIcon, listwidget: QListWidget):
          dirItem = QListWidgetItem(listwidget)
          dirItem.setText(dirname)
          dirItem.setIcon(icon)
          listwidget.addItem(dirItem)
          return dirItem
     



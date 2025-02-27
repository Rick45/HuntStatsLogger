from PyQt6.QtWidgets import QMainWindow, QStatusBar, QApplication
from PyQt6.QtCore import QPoint, Qt

from MainWindow.Main.MainFrame import MainFrame
from Widgets.SystemTrayIcon import SystemTrayIcon
import sys
from resources import settings, resource_path


class MainWindow(QMainWindow):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("MainWindow")
        self.setWindowTitle("Hunt Stats Logger")

        # move window to last known position / size
        # fixed by @monsterdhal
        if settings.value("geometry") != None:
            self.restoreGeometry(settings.value("geometry"))
        if settings.value("windowState") != None:
            self.restoreState(settings.value("windowState"))

        #if settings.value("window_position", "") != "":
            #self.move(settings.value("window_position"))
        #if settings.value("window_size", "") != "":
            #size = settings.value("window_size")
            #self.resize(size.width(),size.height())

        self.mainframe = MainFrame(self)
        self.setCentralWidget(self.mainframe)
        self.setStatusBar(QStatusBar())
        self.statusBar().font().setPixelSize(16)
        self.statusBar().setSizeGripEnabled(True)

        self.setContentsMargins(0,0,0,0)
        self.layout().setSpacing(0)

        self.show()

        self.offset = QPoint()
        self.mousePressed = False
        self.isMini = False
        self.wasMax = False

        self.showSysTray = settings.value("show_sys_tray","False").lower() == "true"
        
        self.sysTrayIco = SystemTrayIcon(self)

    def setStatus(self, msg):
        self.statusBar().showMessage(msg)

    def closeEvent(self, a0):
        if self.mainframe.settingsWindow:
            self.mainframe.settingsWindow.close()
        if self.mainframe.mapWindow:
            self.mainframe.mapWindow.close()

        #self.mainframe.logger.running = False
        #pos = self.mapToGlobal(QPoint(0,0))
        # fixed by @monsterdhal
        if not self.isMini:
            settings.setValue("geometry",self.saveGeometry())
            settings.setValue("windowState",self.saveState())
            #settings.setValue("window_position", pos)
            #settings.setValue("window_size", self.size())
        if not self.showSysTray:
            self.sysTrayIco.setParent(None)
            self.sysTrayIco.deleteLater()
            self.sysTrayIco.hide()
            self.deleteLater()
            sys.exit()
        return super().closeEvent(a0)

    def minify(self):
        self.isMini = True
        if self.isMaximized():
            self.showNormal()
            self.wasMax = True
        settings.setValue("window_size", self.size())
        self.mainframe.tabs.setVisible(False)
        #self.mainframe.buttons.setVisible(False)
        self.statusBar().setVisible(False)
        for i in range(10):
            QApplication.processEvents()
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint,True)
        self.resize(self.minimumSizeHint())
        self.show()
    
    def maxify(self):
        self.isMini = False
        self.mainframe.tabs.setVisible(True)
        self.statusBar().setVisible(True)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint,False)
        if self.wasMax:
            self.showMaximized()
        elif settings.value("window_size", "") != "":
            size = settings.value("window_size")
            self.resize(size.width(),size.height())
        else:
            self.resize(self.minimumSizeHint())
        self.show()


    def mousePressEvent(self, a0) -> None:
        if self.isMini:
            self.mousePressed = True
            self.offset = a0.scenePosition()
        return super().mousePressEvent(a0)

    def mouseReleaseEvent(self, a0) -> None:
        self.mousePressed = False
        return super().mouseReleaseEvent(a0)

    def mouseMoveEvent(self, a0) -> None:
        if(self.mousePressed):
            self.move(
                int(a0.globalPosition().x()) - int(self.offset.x()),
                int(a0.globalPosition().y()) - int(self.offset.y())
            )
        return super().mouseMoveEvent(a0)

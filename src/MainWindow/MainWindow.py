from PyQt6.QtWidgets import QMainWindow, QStatusBar

from MainWindow.MainFrame import MainFrame
from resources import settings

class MainWindow(QMainWindow):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("MainWindow")
        self.setWindowTitle("Hunt Stats Logger")
        self.mainframe = MainFrame(self)
        self.setCentralWidget(self.mainframe)
        self.setStatusBar(QStatusBar())
        self.statusBar().font().setPixelSize(16)
        self.statusBar().setSizeGripEnabled(True)

        if settings.value("window_position","") != "":
            self.move(settings.value("window_position"))


    def setStatus(self,msg):
        self.statusBar().showMessage(msg)

    def closeEvent(self, a0):
        if self.mainframe.settingsWindow:
            self.mainframe.settingsWindow.close()
        if self.mainframe.mapWindow:
            self.mainframe.mapWindow.close()
        self.mainframe.logger.running = False
        settings.setValue("window_position",self.pos())
        return super().closeEvent(a0)
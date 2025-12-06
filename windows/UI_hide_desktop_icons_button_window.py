import subprocess
import time
import winreg
from PySide6.QtWidgets import QVBoxLayout, QLabel
from PySide6.QtCore import QTimer
import functions.ImageQt
from getResources import PREFERENCES
from functions.generateUIImages import generateImage
import threading

from windows.UI_button_window import UIButtonWindow
from windows.functions import hideDesktopIcons



class UI_HideDesktopIconsButtonWindow(UIButtonWindow):
    def __init__(self, screenSize):
        images=generateImage("HideDesktopIcons")
        self.images0=[i.resize(tuple(int(x*PREFERENCES["hideDesktopIconsButtonProportion"]) for x in i.size)) for i in images]
        self.number=0 #visable
        self.border=PREFERENCES["hideDesktopIconsButtonBorder"]

        super().__init__(screenSize)

        self.size0=self.images0[0].size
        self.images=[functions.ImageQt.toqpixmap(i) for i in self.images0]

        layout=QVBoxLayout()
        self.buttonLabel=QLabel(self)
        self.buttonLabel.setPixmap(self.images[self.number])
        self.buttonLabel.setGeometry(0, 0,  *self.size0)
        self.setGeometry(screenSize[0]-self.size0[0]-self.border[0], self.border[1], *self.size0)
        layout.addWidget(self.buttonLabel)

    def change(self):
        self.number= 0 if self.number == 1 else 1
        self.changeThread=threading.Thread(target=hideDesktopIcons, args=[self.number])
        self.canChange=False
        self.changeThread.start()

        self.fixedupdate = QTimer(self)
        self.fixedupdate.timeout.connect(self.frameUpdate)
        self.startt=self.order=0
        self.fixedupdate.start(1000/30)

        self.buttonLabel.setPixmap(self.images[self.number])
        self.canChange=True

if __name__ == '__main__':
    _=UI_HideDesktopIconsButtonWindow()
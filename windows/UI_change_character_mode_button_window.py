from PySide6.QtWidgets import QVBoxLayout, QLabel
from PySide6.QtCore import Qt, QTimer
import functions.ImageQt
from getResources import PREFERENCES
from functions.generateUIImages import generateImage

import time

from windows.UI_button_window import UIButtonWindow



class UI_ChangeCharacterModeButtonWindow(UIButtonWindow):
    def __init__(self, screenSize):
        images=generateImage("ChangeCharacterMode")
        self.images0=[i.resize(tuple(int(x*PREFERENCES["changeCharacterModeButtonProportion"]) for x in i.size)) for i in images]
        self.number=1
        self.border=PREFERENCES["changeCharacterModeButtonBorder"]

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
        #changeThread=threading.Thread(target=hideDesktopIcons, args=[self.number])
        #self.canChange=False
        #changeThread.start()

        self.fixedupdate = QTimer(self)
        self.fixedupdate.timeout.connect(self.frameUpdate)
        self.startt=self.order=0
        self.fixedupdate.start(1000/30)

        self.buttonLabel.setPixmap(self.images[self.number])


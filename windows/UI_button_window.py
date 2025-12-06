from PySide6.QtWidgets import QVBoxLayout
from custom_QDialog import CustomQDialog as QDialog
from PySide6.QtCore import Qt
from animation.animation_player import AnimationPlayer

import time
import threading

class UIButtonWindow(QDialog):
    def __init__(self, screenSize):
        super().__init__()
        self.layout=QVBoxLayout()
        # 设置无边框和透明背景
        self.setWindowModality(Qt.NonModal)
        self.setWindowFlags(Qt.FramelessWindowHint|Qt.ToolTip)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        self.buttonAnim=AnimationPlayer("UIAni_Button_Scale")
        self.canChange=True
        
        self.playable=False

    def frameUpdate(self):
        if hasattr(self, 'changeThread'):
            self.canChange=not self.changeThread.isAlive()

        if self.startt==0 and not self.playable:
            self.pos0 = (self.frameGeometry().topLeft().x(), self.frameGeometry().topLeft().y())
            self.centerpos0=[x+y//2 for x,y in zip(self.pos0, self.size0)]
        if self.order == 0:
            result, self.playable = self.buttonAnim.play_frame(time.time() - self.startt)
            if not self.playable:
                self.order += 1
                self.startt=time.time()
        if self.order == 1:
            result, self.playable = self.buttonAnim.play_frame(time.time() - self.startt, timeReverse=True)

        if self.playable: 
            size=tuple(x*y for x,y in zip(result['scale'], self.size0))
            currentPixmap=self.images[self.number].scaled(*size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.buttonLabel.setPixmap(currentPixmap)
            self.setGeometry(*[x-y//2 for x,y in zip(self.centerpos0, size)], *size)
            self.buttonLabel.setFixedSize(*size)
        else:
            self.buttonLabel.setPixmap(self.images[self.number])
            self.setGeometry(*self.pos0, *self.size0)
            self.buttonLabel.setFixedSize(*self.size0)
    
    def mousePressEvent(self, event):
        if self.canChange:
            self.change()
    #def whenClose(self):
    #    changeThread=threading.Thread(target=hideDesktopIcons, args=[0])
    #    changeThread.start()
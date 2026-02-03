from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, Signal
from animation.pyside_animation_player import PysideAnimationPlayer

import time

from windows.UI_dark_screen_window import UI_DarkScreenWindow


class UI_PopupWindow(QWidget):
    anim_signal = Signal(dict)

    def __init__(self, darkScreen=True):
        super().__init__()
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.darkScreenWindow = None
        if darkScreen:
            self.darkScreenWindow = UI_DarkScreenWindow()
            self.darkScreenWindow.show()

    def play_anim(self, anim='AnimationClip/UIAni_Popup_System.anim', **kwargs):
        if anim == 'AnimationClip/UIAni_Popup_System.anim':
            kwargs.setdefault('path', 'Center/Popup')
            kwargs.setdefault('Pratio', (1, 0.5))

        self.position0 = (self.pos().x(), self.pos().y())
        self.move(10000, 10000)
        self.show()

        self.anim_signal.connect(self.anim_signal_received)
        self.animation_player = PysideAnimationPlayer(self.anim_signal, anim, kwargs.get('stop_time', None), **kwargs)
        self.animation_player.play()

    def anim_signal_received(self, dic):
        position = dic.get('position', (0, 0))
        self.move(*[int(x - y) for x, y in zip(self.position0, position)])

    def closeEvent(self, event):
        self.darkScreenWindow.close()

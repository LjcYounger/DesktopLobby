from PySide6.QtWidgets import QLineEdit, QHBoxLayout, QPushButton, QDialog
from PySide6.QtCore import Qt

from signal_bus import signal_bus

# TODO() 增加剧情式对话框
class UI_InputWindow_classic(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint|Qt.WindowStaysOnTopHint)
        #self.setAttribute(Qt.WA_TranslucentBackground, True)
        sw, sh = self.screen().geometry().width(), self.screen().geometry().height()
        self.setFixedWidth(sw*0.95)
        self.move(sw*0.025-5, sh-110)

        layout=QHBoxLayout()

        self.textbox=QLineEdit()
        self.textbox.setFixedSize(sw*0.85, 35)
        self.textbox.setStyleSheet("font-size: 22px")
        layout.addWidget(self.textbox)

        confirmbutton=QPushButton()
        confirmbutton.setText("confirm")
        confirmbutton.setFixedHeight(35)
        layout.addWidget(confirmbutton)
        
        self.setLayout(layout)

        confirmbutton.pressed.connect(lambda: self.press())

    def press(self):
        content = self.textbox.text()
        print(f"[DEBUG]Input Content: {content}")
        self.textbox.setText("")
        self.hide()
        signal_bus.AI_dialog_input_signal.emit(content)
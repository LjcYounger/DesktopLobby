from PySide6.QtWidgets import QVBoxLayout, QLabel, QLineEdit, QHBoxLayout, QPushButton
from PySide6.QtCore import Qt
from windows.UI_popup_window import UI_PopupWindow
from functions.birthday import setBirthdayDate

from windows.functions import verifyDate
from getResources import GLOBAL_CONFIG

class UI_EnterBirthdayDateWindow(UI_PopupWindow):
    def __init__(self, screenSize) -> None:
        super().__init__()
        self.setWindowTitle("Notice")
        self.setWindowFlag(Qt.WindowType.WindowMaximizeButtonHint, False)
        self.setFixedSize(400,210)
        center=self.screen().availableGeometry().center()
        self.move(center.x()-410/2, center.y()-210/2)
        #self.setStyleSheet("QMainWindow::titlebar {text-align: center;}")
        layout=QVBoxLayout()
        #layout.addStretch()

        h_layout1 = QHBoxLayout()
        h_layout1.addStretch()
        self.textbox=QLabel()
        self.textbox.setText(GLOBAL_CONFIG.LANGUAGE.get("Birthday", ""))
        self.textbox.setAlignment(Qt.AlignmentFlag.AlignCenter)  # 文本居中
        self.textbox.setFixedSize(210,20)           # 固定宽度200px
        self.textbox.setStyleSheet("background-color: #456397; padding: 1px; color: #ffffff;")
        h_layout1.addWidget(self.textbox)
        h_layout1.addStretch()

        h_layout2 = QHBoxLayout()
        h_layout2.addStretch()
        self.datebox = QLineEdit()
        self.datebox.setPlaceholderText("MMDDYYYY")
        self.datebox.setMaxLength(8)
        self.datebox.setFixedWidth(210)
        self.datebox.setStyleSheet("color: #456397;")
        self.datebox.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.datebox.setFocusPolicy(Qt.ClickFocus)
        h_layout2.addWidget(self.datebox)
        h_layout2.addStretch()

        h_layout3 = QHBoxLayout()
        h_layout3.addStretch()
        self.textbox=QLabel()
        self.textbox.setText(GLOBAL_CONFIG.LANGUAGE.get("BirthdayTip", ""))
        self.textbox.setStyleSheet("color: #456397;")
        self.textbox.setAlignment(Qt.AlignmentFlag.AlignCenter)  # 文本居中          # 固定宽度200px
        h_layout3.addWidget(self.textbox)
        h_layout3.addStretch()


        h_layout4 = QHBoxLayout()
        h_layout4.addStretch()
        self.button = QPushButton()
        self.button.setText("OK")
        self.button.setStyleSheet("color: #456397;")
        self.button.setFixedSize(120,40)
        self.button.clicked.connect(self.verify)
        h_layout4.addWidget(self.button)
        h_layout4.addStretch()

        layout.addLayout(h_layout1)
        layout.addLayout(h_layout2)
        layout.addLayout(h_layout3)
        layout.addLayout(h_layout4)
        self.setLayout(layout)

        self.closable=False

        self.play_anim()

    def verify(self):
        time=self.datebox.text()
        result=verifyDate(time)
        if result:
            setBirthdayDate(time[:2]+'-'+time[2:4])
            self.closable=True
            self.close()
        else:
            _=UI_EBSW_ErrorWindow()
class UI_EBSW_ErrorWindow(UI_PopupWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Notice")
        self.setWindowFlag(Qt.WindowType.WindowMaximizeButtonHint, False)
        self.setWindowModality(Qt.ApplicationModal)
        self.setFixedSize(250,120)
        center=self.screen().availableGeometry().center()
        self.move(center.x()-250/2, center.y()-120/2)

        layout=QVBoxLayout()
        #layout.addStretch()

        h_layout1 = QHBoxLayout()
        h_layout1.addStretch()
        self.textbox=QLabel()
        self.textbox.setText("Please enter your\n8-digit date of birth accurately.")
        self.textbox.setStyleSheet("color: #456397;")
        self.textbox.setAlignment(Qt.AlignmentFlag.AlignCenter)  # 文本居中          # 固定宽度200px
        h_layout1.addWidget(self.textbox)
        h_layout1.addStretch()


        h_layout2 = QHBoxLayout()
        h_layout2.addStretch()
        self.button = QPushButton()
        self.button.setText("OK")
        self.button.setStyleSheet("color: #456397;")
        self.button.setFixedSize(120,40)
        self.button.clicked.connect(lambda: self.close())
        h_layout2.addWidget(self.button)
        h_layout2.addStretch()

        layout.addLayout(h_layout1)
        layout.addLayout(h_layout2)
        self.setLayout(layout)

        self.play_anim()

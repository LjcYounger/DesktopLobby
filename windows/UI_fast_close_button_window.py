from custom_QDialog import CustomQDialog as QDialog
from PySide6.QtWidgets import QHBoxLayout, QPushButton
from PySide6.QtCore import Qt
from getResources import GLOBAL_CONFIG
from signal_bus import signal_bus


class UI_FastCloseButtonWindow(QDialog):
    def __init__(self):
        super().__init__()
        # 设置无边框和透明背景
        self.setWindowFlags(Qt.FramelessWindowHint|Qt.WindowStaysOnTopHint|Qt.ToolTip)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        
        sw, sh = self.screen().geometry().width(), self.screen().geometry().height()
        button_size = (100, 42)
        button_border = GLOBAL_CONFIG.PREFERENCES["fastCloseButtonBorder"]
        self.setGeometry(sw-button_size[0]-10-button_border[0], 
                         sh-button_size[1]-10-button_border[1], *button_size)

        layout=QHBoxLayout()

        close_button=QPushButton()
        close_button.setText("CLOSE")
        close_button.setFixedSize(*button_size)
        close_button.setStyleSheet("font-size: 20px")
        layout.addWidget(close_button)
        
        self.setLayout(layout)

        close_button.pressed.connect(lambda: signal_bus.close_signal.emit())
        
if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)
    c=UI_FastCloseButtonWindow()
    c.show()
    sys.exit(app.exec_())
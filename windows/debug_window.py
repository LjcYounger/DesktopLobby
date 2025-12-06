import sys
from PySide6.QtWidgets import QDialog, QVBoxLayout, QPlainTextEdit
from PySide6.QtGui import QTextCharFormat, QColor
from signal_bus import signal_bus

# 步骤1: 创建一个重定向输出的类
class PrintToSignal:
    def write(self, text):
        # 将文本追加到控件中
        signal_bus.print_signal.emit(text)

    def flush(self):
        # 兼容文件对象接口，这里可以什么都不做
        pass

class DebugWindow(QDialog):
    def __init__(self, font):
        super().__init__()
        self.font = font

        self.setWindowTitle("Debug Window")
        self.setGeometry(0, 0, 400, 200)
        layout = QVBoxLayout(self)

        # 创建用于显示print内容的控件
        self.log_output = QPlainTextEdit(self)
        self.log_output.setReadOnly(True)
        layout.addWidget(self.log_output)
        self.setLayout(layout)

        self.cursor = self.log_output.textCursor()

        # 将sys.stdout重定向到PrintToWidget实例
        signal_bus.print_signal.connect(self.print)
        self.redirector = PrintToSignal()
        sys.stdout = self.redirector

    def print(self, text):
        level_dict = {"DEBUG": "green", "ERROR": "red", "WARNING": "yellow", "": "black"}
        for level in level_dict.keys():
            if text.startswith(f"[{level}]"):
                self._write(text, QColor(level_dict[level]))

    def _write(self, text: str, color: QColor):
        fmt = QTextCharFormat()
        fmt.setForeground(color)
        fmt.setFont(self.font)

        self.cursor.movePosition(self.cursor.End)
        self.cursor.insertText(text + "\n", fmt)
        self.log_output.setTextCursor(self.cursor)
        self.log_output.ensureCursorVisible()

        signal_bus.debug_show_signal.connect(self._show_window)

    def _show_window(self, state):
        if state:
            self.show()
        else:
            self.hide()
from PySide6.QtWidgets import QDialog
from signal_bus import signal_bus


class CustomQDialog(QDialog):
    def __init__(self):
        super().__init__()
        signal_bus.close_signal.connect(lambda: self.hide())

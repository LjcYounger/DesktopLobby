from PySide6.QtWidgets import QVBoxLayout, QWidget, QLabel, QApplication, QMessageBox, QLineEdit, QHBoxLayout, QPushButton, QDialog
from PySide6.QtCore import Qt, QTimer
import functions.ImageQt
from getResources import PREFERENCES, setBirthdayDate
from animation_player import animation_player
from functions.generateUIImages import generateImage
from attachedWindows import Communicator
import sys

import time
import winreg
import subprocess
import threading













if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)
    c=UI_InputWindow_classic()
    c.show()
    sys.exit(app.exec_())
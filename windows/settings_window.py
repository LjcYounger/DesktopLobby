from PySide6.QtCore import Qt, QTimer
from custom_QDialog import CustomQDialog as QDialog
from PySide6.QtWidgets import (QLabel,
                            QVBoxLayout,
                            QComboBox,
                            QCheckBox,
                            QSlider,
                            QLineEdit,
                            QPushButton,
                            QHBoxLayout)
import pygame.mixer as mixer
from getResources import GLOBAL_CONFIG, getCurrentCharacter
from windows.AI_settings_window import AISettingsWindow
from signal_bus import signal_bus

class SettingsWindow(QDialog):
    def __init__(self, CNAME, EMOTIONS, SETTINGS, k00):
        super().__init__()
        self.setWindowTitle('Settings')
        self.setGeometry(100, 100, 200, 150)
        #self.setWindowFlags(Qt.Tool)

        layout=QVBoxLayout()

        self.emotionCombo = QComboBox()
        self.emotionCombo.addItems(EMOTIONS)
        self.emotionCombo.setCurrentIndex(SETTINGS['defaultEmotionIndex'])
        layout.addWidget(self.emotionCombo)

        self.blinkCheck = QCheckBox(GLOBAL_CONFIG.LANGUAGE.get("Blinking eyes", ""), self)
        self.blinkCheck.setChecked(SETTINGS['defaultBlinkEyes'])
        layout.addWidget(self.blinkCheck)

        self.dialogCheck = QCheckBox(GLOBAL_CONFIG.LANGUAGE.get("Dialog", ""), self)
        self.dialogCheck.setChecked(SETTINGS['defaultDialog'])
        layout.addWidget(self.dialogCheck)

        moveCheck = QCheckBox(GLOBAL_CONFIG.LANGUAGE.get("Movable", ""), self)
        moveCheck.setChecked(False)
        layout.addWidget(moveCheck)

        layout.addStretch(1)

        l1=QHBoxLayout()

        sizemessage = QLabel(GLOBAL_CONFIG.LANGUAGE.get('Size', ""))
        l1.addWidget(sizemessage)

        self.Sslider = QSlider(Qt.Horizontal)
        self.Sslider.setMinimum(1000)
        self.Sslider.setMaximum(30000)
        self.Sslider.setSingleStep(1)
        self.Sslider.setValue(int(k00 *10000))
        l1.addWidget(self.Sslider)

        self.numbox = QLineEdit()
        self.numbox.setText(str(k00))
        self.numbox.setFixedWidth(38)
        l1.addWidget(self.numbox)

        layout.addLayout(l1)

        closeCheck = QCheckBox(GLOBAL_CONFIG.LANGUAGE.get("Closable", ""), self)
        closeCheck.setChecked(True)
        layout.addWidget(closeCheck)

        levelCheck = QCheckBox(GLOBAL_CONFIG.LANGUAGE.get("Always at the Top Level", ""), self)
        levelCheck.setChecked(False)
        layout.addWidget(levelCheck)

        layout.addStretch(1)

        message1 = QLabel(GLOBAL_CONFIG.LANGUAGE.get('BGM volume', ""))
        layout.addWidget(message1)

        self.Bslider = QSlider(Qt.Horizontal)
        self.Bslider.setMinimum(0)
        self.Bslider.setMaximum(100)
        self.Bslider.setSingleStep(1)
        self.Bslider.setValue(GLOBAL_CONFIG.PREFERENCES["defaultBGMVolume"]*100)
        layout.addWidget(self.Bslider)

        message2 = QLabel(GLOBAL_CONFIG.LANGUAGE.get('Voice volume', ""))
        layout.addWidget(message2)

        self.Vslider = QSlider(Qt.Horizontal)
        self.Vslider.setMinimum(0)
        self.Vslider.setMaximum(100)
        self.Vslider.setSingleStep(1)
        self.Vslider.setValue(GLOBAL_CONFIG.PREFERENCES["defaultVoiceVolume"]*100)
        layout.addWidget(self.Vslider)

        characterCombo = QComboBox()
        fixedNames=[GLOBAL_CONFIG.CONTRAST.get(x, x) if GLOBAL_CONFIG.CONTRAST.get(x, x).isupper() else GLOBAL_CONFIG.CONTRAST.get(x, x).capitalize() for x in GLOBAL_CONFIG.CODE_NAMES]
        fixedNames=[GLOBAL_CONFIG.LANGUAGE.get(x, x) for x in fixedNames]
        characterCombo.addItems(fixedNames)
        currentcharacter=getCurrentCharacter()
        currentChar_eng=GLOBAL_CONFIG.CONTRAST.get(currentcharacter, currentcharacter).capitalize()
        characterCombo.setCurrentText(GLOBAL_CONFIG.LANGUAGE.get(currentChar_eng, currentChar_eng))
        layout.addWidget(characterCombo)

        sizemessage1 = QLabel(GLOBAL_CONFIG.LANGUAGE.get("Experimental Features", ""))
        layout.addWidget(sizemessage1)

        AIONTButton = QPushButton()
        AIONTButton.setText(GLOBAL_CONFIG.LANGUAGE.get("Start a New Topic", ""))
        layout.addWidget(AIONTButton)

        AIsettingsButton = QPushButton()
        AIsettingsButton.setText(GLOBAL_CONFIG.LANGUAGE.get("AI settings", ""))
        layout.addWidget(AIsettingsButton)

        self.setLayout(layout)

        self.AIsettingwindow=AISettingsWindow(CNAME)


        self.emotionCombo.currentIndexChanged.connect(lambda: self.send_signal('emotion', self.emotionCombo.currentText()))
        self.blinkCheck.stateChanged.connect(lambda state: self.send_signal('blink', state))
        self.dialogCheck.stateChanged.connect(lambda state: self.send_signal('dialog', state))
        moveCheck.stateChanged.connect(lambda state: self.send_signal('move', state))
        closeCheck.stateChanged.connect(lambda state: self.send_signal('close', state))
        levelCheck.stateChanged.connect(lambda state: self.send_signal('top_level', state))

        self.Sslider.valueChanged.connect(self.update_numbox)
        self.Sslider.sliderReleased.connect(self.send_size_final)
        self.numbox.textChanged.connect(self.update_Sslider_and_send_final)

        self.Bslider.valueChanged.connect(lambda value: self.send_signal('bgm_volume', value/100))
        self.Vslider.valueChanged.connect(lambda value: self.send_signal('voice_volume', value/100))

        characterCombo.currentIndexChanged.connect(lambda: self.send_signal('character', GLOBAL_CONFIG.CODE_NAMES[characterCombo.currentIndex()]))

        AIONTButton.pressed.connect(lambda: self.send_signal('AI_open_new_topic', 1))
        AIsettingsButton.pressed.connect(lambda: self.AIsettingwindow.show())
        self.timer=QTimer(self)
        self.timer.timeout.connect(self.update_canchange)
        self.canchange=True
        self.timer.start(30)
        

    def send_signal(self, key: str, value):
        signal_bus.settings_signal.emit(key, value)

    def update_canchange(self): self.canchange=True

    def update_numbox(self, value):
        double_value = value / 10000.0
        # 断开数值框信号连接，避免循环触发
        self.numbox.textChanged.disconnect()
        self.numbox.setText(str(double_value))
        # 重新连接信号
        self.numbox.textChanged.connect(self.update_Sslider_and_send_final)
        if self.canchange:
            self.send_signal('size_preview', double_value)
            self.canchange=False

    def update_Sslider(self, value):
        if self.canchange:
            try:
                fvalue=min(max(float(value), 0.1), 3.0)
                int_value = int(fvalue * 10000)
                # 断开滑动条信号连接，避免循环触发
                self.Sslider.valueChanged.disconnect()
                self.Sslider.setValue(int_value)
                # 重新连接信号
                self.Sslider.valueChanged.connect(self.update_numbox)
                self.numbox.setText(str(fvalue))
                #self.Sizecommunicator.data_signal.emit(fvalue)
            except ValueError:
                pass
    
    # 新增：处理数字输入框修改并发送最终信号
    def update_Sslider_and_send_final(self, value):
        if self.canchange:
            try:
                fvalue=min(max(float(value), 0.1), 3.0)
                int_value = int(fvalue * 10000)
                # 断开滑动条信号连接，避免循环触发
                self.Sslider.valueChanged.disconnect()
                self.Sslider.setValue(int_value)
                # 重新连接信号
                self.Sslider.valueChanged.connect(self.update_numbox)
                self.numbox.setText(str(fvalue))
                self.send_signal('size_final', fvalue)  # 发送最终信号
            except ValueError:
                pass
    
    # 新增：发送尺寸最终信号
    def send_size_final(self):
        value = self.Sslider.value() / 10000.0
        self.send_signal('size_final', value)
    
    # 移除了 stop_preview_timer 和 restart_preview_timer 方法

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QLabel, QVBoxLayout
from custom_QDialog import CustomQDialog as QDialog
import functions.ImageQt
import pygame.mixer as mixer
import time
from getResources import PREFERENCES
from windows.functions import setopacity
from audios.sound import load_audio_file
from signal_bus import signal_bus
from getResources import GLOBAL_CONFIG


class DialogBoxWindow(QDialog):
    def __init__(self, name, dialogBoxImages, EMOTIONS, SETTINGS, k00, imageWindow):
        super().__init__()
        self.EMOTIONS = EMOTIONS
        self.SETTINGS = SETTINGS
        self.name = name
        self.dialogBoxImages = dialogBoxImages
        self.imageWindowP = imageWindow

        self.k = k00
        self.voiceVolume = PREFERENCES["defaultVoiceVolume"]
        self.aniName = None

        layout = QVBoxLayout()
        # 设置无边框和透明背景
        self.setWindowModality(Qt.NonModal)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.ToolTip)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setGeometry(SETTINGS["dialogBoxPos"][0] * self.k / GLOBAL_CONFIG.ZOOM_SCALE,
                         SETTINGS["dialogBoxPos"][1] * self.k / GLOBAL_CONFIG.ZOOM_SCALE, 1, 1)
        self.boxlabel = QLabel(self)
        self.boxlabel.setGeometry(0, 0, 1, 1)
        layout.addWidget(self.boxlabel)

        self.textlabel = QLabel(self)
        self.textlabel.setGeometry(0, 0, 1, 1)
        layout.addWidget(self.textlabel)

    def vvolumeChanged(self, data):
        self.voiceVolume = data / 100

    def showDB(self, indexes, emotions, custom=False, custom_dialogboxs=None, order=0, lasting_time=None):
        self.indexes = indexes
        self.emotions = emotions
        self.order = order
        index = self.indexes[self.order]
        if '|' in index:
            index, self.aniName = index.split('|')
        else:
            self.aniName = None
        self.emotion = self.emotions[self.order]
        if custom:
            self.dialogBox0 = custom_dialogboxs[self.order][0]
            dialogBox = self.dialogBox0.resize(
                tuple(int(x * self.k / GLOBAL_CONFIG.ZOOM_SCALE) for x in self.dialogBox0.size))
            self.dialogText0 = custom_dialogboxs[self.order][1]
            dialogText = self.dialogText0.resize(
                tuple(int(x * self.k / GLOBAL_CONFIG.ZOOM_SCALE) for x in self.dialogText0.size))
        else:
            self.dialogBox0 = self.dialogBoxImages[index][0]
            dialogBox = self.dialogBox0.resize(
                tuple(int(x * self.k / GLOBAL_CONFIG.ZOOM_SCALE) for x in self.dialogBox0.size))
            self.dialogText0 = self.dialogBoxImages[index][1]
            dialogText = self.dialogText0.resize(
                tuple(int(x * self.k / GLOBAL_CONFIG.ZOOM_SCALE) for x in self.dialogText0.size))
        PdialogBox = functions.ImageQt.toqpixmap(dialogBox)
        PdialogText = functions.ImageQt.toqpixmap(dialogText)
        self.order += 1
        if self.order == len(self.indexes):
            self.end = True
        else:
            self.end = False
        self.boxlabel.setPixmap(PdialogBox)
        self.boxlabel.setGeometry(0, 0, dialogBox.width, dialogBox.height)
        self.textlabel.setPixmap(PdialogText)
        self.textlabel.setGeometry(0, 0, dialogText.width, dialogText.height)
        if self.order == 1:
            setopacity(self.boxlabel, 0)
            setopacity(self.textlabel, 0)

        self.dialoging = self.emotionchange = True
        self.t0 = 0
        mixer.stop()

        namefile = self.name if self.name.isupper() else self.name.capitalize()
        if not custom:
            self.voice = load_audio_file(f"audios/JP_{namefile}/{self.name}_{index}.ogg")
            self.voice.set_volume(self.voiceVolume)
            self.voice.play()

        if lasting_time:
            self.length = lasting_time
        else:
            self.length = max(self.voice.get_length(), 1)
        self.fixedupdate = QTimer(self)
        self.fixedupdate.timeout.connect(self.frameUpdate)
        self.show()
        if self.aniName:
            signal_bus.dialog_anim_signal.emit(self.aniName)
        self.fixedupdate.start(1000 / 30)

    def frameUpdate(self, fadeIn=0.6, fadeOut=0.6):
        self.voice.set_volume(self.voiceVolume)
        if self.t0 == 0:
            self.t0 = time.time()
            t = 0
            self.sizeposChange(self.k)
            self.tempCanblink = getattr(self.imageWindowP.settings_parameters, 'blink')
            signal_bus.settings_signal.emit('blink', False)
            self.imageWindowP.update(self.emotion)
        else:
            t = time.time() - self.t0
        if self.dialoging and self.imageWindowP.settings_parameters.dialog:
            if 0 <= t and t <= fadeIn:
                if self.order == 1:
                    setopacity(self.boxlabel, t / fadeIn)
                else:
                    setopacity(self.boxlabel, 1)
                setopacity(self.textlabel, t / fadeIn)
            elif fadeIn < t and t <= self.length:
                setopacity(self.boxlabel, 1)
                setopacity(self.textlabel, 1)
            elif self.length < t and t <= self.length + fadeOut:
                if self.emotionchange and self.end:
                    self.imageWindowP.update(self.EMOTIONS[self.SETTINGS['defaultEmotionIndex']])
                    signal_bus.settings_signal.emit('blink', self.tempCanblink)
                    self.emotionchange = False
                if self.end:
                    setopacity(self.boxlabel, (self.length + fadeOut - t) / fadeOut)
                else:
                    setopacity(self.boxlabel, 1)
                setopacity(self.textlabel, (self.length + fadeOut - t) / fadeOut)
            else:
                setopacity(self.boxlabel, 0)
                setopacity(self.textlabel, 0)
                t = self.length + fadeOut + 1
                self.hide()
                self.dialoging = False
        elif not self.end:
            self.showDB(self.indexes, self.EMOTIONS, order=self.order)
        elif self.emotionchange:
            self.voice.stop()
            self.hide()
            setopacity(self.boxlabel, 0)
            setopacity(self.textlabel, 0)
            self.imageWindowP.update(self.EMOTIONS[self.SETTINGS['defaultEmotionIndex']])
            signal_bus.settings_signal.emit('blink', self.tempCanblink)
            self.emotionchange = self.dialoging = False

    def sizeposChange(self, data):
        self.k = data
        dialogBox = self.dialogBox0.resize(
            tuple(int(x * self.k / GLOBAL_CONFIG.ZOOM_SCALE) for x in self.dialogBox0.size))
        dialogText = self.dialogText0.resize(
            tuple(int(x * self.k / GLOBAL_CONFIG.ZOOM_SCALE) for x in self.dialogText0.size))
        PdialogBox = functions.ImageQt.toqpixmap(dialogBox)
        PdialogText = functions.ImageQt.toqpixmap(dialogText)
        self.boxlabel.setPixmap(PdialogBox)
        self.textlabel.setPixmap(PdialogText)

        self.boxlabel.setFixedSize(dialogBox.width, dialogBox.height)
        self.textlabel.setFixedSize(dialogText.width, dialogText.height)

        charactercenter = self.imageWindowP.frameGeometry().center()
        self.setGeometry(charactercenter.x() + (self.SETTINGS["dialogBoxPos"][0] - self.SETTINGS['characterPos'][
            0]) * self.k / GLOBAL_CONFIG.ZOOM_SCALE - self.imageWindowP.size0[0] / 2 * self.k,
                         charactercenter.y() + (self.SETTINGS["dialogBoxPos"][1] - self.SETTINGS['characterPos'][
                             1]) * self.k / GLOBAL_CONFIG.ZOOM_SCALE - self.imageWindowP.size0[1] / 2 * self.k,
                         dialogBox.width, dialogBox.height)

    def closeEvent(self, event):
        event.ignore()

from PyQt5.QtCore import Qt, QTimer, QObject, pyqtSignal, QThread
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QMainWindow, QComboBox, QCheckBox, QDialog, QSlider, QLineEdit, QApplication, QDesktopWidget, QWidget, QMessageBox, QGraphicsOpacityEffect
from PIL import ImageQt
import sys
import time
import pygame as pg
from random import randrange
from math import sin
import os
import socket
import signal
import importlib.util
from getResources import *
from renderDialogBox import *
from playAnims import PlayAnims
names=getCharacterNames()
perferences=getPerferences()
contrast=getContrast()
pg.init()
pg.mixer.init()

app = QApplication(sys.argv)
app.setQuitOnLastWindowClosed(True)
screen = QDesktopWidget().screenGeometry()
k00=min(screen.width()/1600, screen.height()/900) * 1.1962
class Communicator(QObject):
    # 创建一个信号类，用于传递数据
    data_signal = pyqtSignal(object)

# 创建一个线程类来监听套接字
class SocketListener(QThread):
    def __init__(self, comm):
        super().__init__()
        self.comm = comm
    def run(self, address=10000):
        # 创建套接字服务器
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(('localhost', address))
            sock.listen(1)
            while True:
                conn, addr = sock.accept()
                data = conn.recv(1024)
                if data:
                    message = data.decode().strip()
                    self.comm.data_signal.emit(message)
                    data=None
                time.sleep(0.2)
        except:
            if address < 10009:
                self.run(address=address+1)

def main(name, firstTime=False):
    perferences=getPerferences()

    scriptpath=os.path.join(os.path.dirname(__file__), "characters", name, "getCharacter.py")
    spec=importlib.util.spec_from_file_location("getCharacter", scriptpath)
    moudle=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(moudle)
    
    pictures, settings = moudle.getCharacter(name)
    haloHeight=settings.get('haloHeight', 100)
    emotions=sorted(pictures.keys())
    emotions.remove('halo')
    k0=settings.get('k', 1)*k00
    dialogBoxContent = getDialogBoxContent(name)
    def setopacity(label, opacity):
        effect=QGraphicsOpacityEffect()
        label.setGraphicsEffect(effect)
        effect.setOpacity(opacity)

    class ImageWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.layout=QVBoxLayout()
            # 设置无边框和透明背景
            self.setWindowFlags(Qt.FramelessWindowHint)
            self.setAttribute(Qt.WA_TranslucentBackground, True)
            
            self.haloPos=settings['halo']
            self.t=0
            self.k=k0
            self.movable=False
            self.closable=True
            self.canblink=settings['defaultBlinkEyes']
            self.candialog=settings['defaultDialog']
            self.vvolume=perferences["defaultVoiceVolume"]
            self.dialogBoxImages={}
            for key, content in dialogBoxContent.items():
                dialogBoxX, dialogTextX = render_Lobby_balloon(content[0])
                self.dialogBoxImages[key] = [dialogBoxX.resize(tuple(int(x*k00/1.1962) for x in dialogBoxX.size)),
                                            dialogTextX.resize(tuple(int(x*k00/1.1962) for x in dialogTextX.size)), content[1]]
            self.anims={}
            for animName in perferences['animNames']:
                self.anims[animName]=PlayAnims(animName)
            self.playable=False
            self.currentEmotion=emotions[settings['defaultEmotionIndex']]
            self.image0=pictures[self.currentEmotion]
            self.haloImage=pictures['halo']
            
            self.halo=QLabel('halo', self)
            self.halo.setPixmap(ImageQt.toqpixmap(self.haloImage))
            self.halo.setFixedSize(self.haloImage.width, self.haloImage.height)
            self.halo.move(self.haloPos[0], self.haloPos[1])
            self.layout.addWidget(self.halo)
            self.size0=(self.image0.width, self.image0.height+haloHeight)
            self.resize(self.size0[0], self.size0[1])

            self.body=QLabel('body', self)
            self.body.setPixmap(ImageQt.toqpixmap(self.image0))
            self.body.setFixedSize(self.image0.width, self.image0.height)
            self.body.move((self.width() - self.image0.width)/2, (self.height() - self.image0.height+haloHeight)/2)
            self.layout.addWidget(self.body)
            self.setLayout(self.layout)
            
            self.move(settings['characterPos'][0] *k00/1.1962, settings['characterPos'][1] *k00/1.1962)
            self.sizeChange(k00)
            self.fixedupdate = QTimer(self)
            self.fixedupdate.timeout.connect(self.frameUpdate)
            self.t0=0
            self.fixedupdate.start(1000/30)
            
            self.dialogboxwindow = DialogBoxWindow(self.dialogBoxImages)
            self.dialogboxwindow.show()

            self.settingwindow = SettingWindow()
            self.settingwindow.Emotioncommunicator.data_signal.connect(self.update)
            self.settingwindow.Blinkcommunicator.data_signal.connect(self.canblinkchanged)
            self.settingwindow.Dialogcommunicator.data_signal.connect(self.candialogchanged)
            self.settingwindow.Movecommunicator.data_signal.connect(self.movablechanged)
            self.settingwindow.Sizecommunicator.data_signal.connect(self.sizeChange)
            self.settingwindow.Sizecommunicator.data_signal.connect(self.dialogboxwindow.sizeposChange)
            self.settingwindow.Closecommunicator.data_signal.connect(self.closablechanged)
            self.settingwindow.Levelcommunicator.data_signal.connect(self.levelchanged)
            self.settingwindow.VVolumecommunicator.data_signal.connect(self.dialogboxwindow.vvolumeChanged)
            self.settingwindow.VVolumecommunicator.data_signal.connect(self.vvolumeChanged)
            self.settingwindow.Charactercommunicator.data_signal.connect(self.characterChanged)
            self.dialogboxwindow.timeCommunicator.data_signal.connect(self.playingAnim)

            self.DFvsHAFcommunicator=Communicator()
            self.DFvsHAFcommunicator.data_signal.connect(self.signalReceived)
            if firstTime:
                try:
                    self.socketThread=SocketListener(self.DFvsHAFcommunicator)
                    self.socketThread.start()
                except:
                    pass
            if self.candialog:
                self.dialog(settings["login"])
        def canblinkchanged(self, data):
            self.canblink = True if data == 2 else False
        def candialogchanged(self, data):
            self.candialog = True if data == 2 else False
        def movablechanged(self, data):
            self.movable = True if data == 2 else False
            self.settingwindow.dialogCheck.setChecked(False)
            self.settingwindow.dialogCheck.setCheckable(not self.movable)
        def closablechanged(self, data):
            self.closable = True if data == 2 else False
        def levelchanged(self, data):
            if data == 2:
                self.setWindowFlags(Qt.FramelessWindowHint|Qt.WindowStaysOnTopHint)
                self.dialogboxwindow.setWindowFlags(Qt.FramelessWindowHint|Qt.Tool|Qt.WindowStaysOnTopHint)
                self.show()
            else:
                self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)
                self.dialogboxwindow.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)
                self.show()
        def vvolumeChanged(self, data):
            self.vvolume=data/100
        def update(self, data, changeCurrentEmotion=True):
            if changeCurrentEmotion:
                self.currentEmotion=data
            self.image0=pictures[data]
            self.image1=self.image0.resize(tuple(int(x*self.k) for x in self.image0.size))
            self.body.setPixmap(ImageQt.toqpixmap(self.image1))

        def frameUpdate(self, blinkingtime=settings['blinkingTime'], deltablinktime=settings['deltaBlinkTime']):
            if self.t0 == 0:
                self.t0 = time.time()
                self.sblinktime=0
            t=time.time()-self.t0
            dy=sin(t/2)*5*self.k/1.1962
            self.halo.move(self.haloPos[0]*self.k, self.haloPos[1]*self.k+dy)
            if self.canblink:
                if t-self.sblinktime > blinkingtime:
                    self.update(self.currentEmotion)
                    self.sblinktime=t+blinkingtime+999999
                if t % deltablinktime < 1/30 or t % deltablinktime > deltablinktime-1/30:
                    self.update("eyeclose", changeCurrentEmotion=False)
                    self.sblinktime=t
        def signalReceived(self, message):
            self.candialog=self.canblink=False
            indexType={'fail': "emotionWhenFailingIndex"}[message]
            try:
                self.settingwindow.dialogCheck.setChecked(False)
                self.settingwindow.blinkCheck.setChecked(False)
                if indexType in settings.keys():
                    self.settingwindow.emotionCombo.setCurrentIndex(settings[indexType])
            except Exception as e:
                print(e)
            self.update(emotions[settings[indexType]] if indexType in settings.keys() else self.currentEmotion)

            try:
                namefile=name if name.isupper() else name.capitalize()
                voice = pg.mixer.Sound(f"audios/JP_{namefile}/{name}_battle_retire.ogg")
            except:
                voice = pg.mixer.Sound("audios/mute.ogg")
            voice.set_volume(self.vvolume)
            voice.play()
        def dialog(self, indexes):
            index=indexes[randrange(0, len(indexes))]
            emotion=[next((s for s in emotions if s.startswith(dialogBoxContent[inde.split('|')[0]][1])), None) for inde in index]
            self.dialogboxwindow.showDB(index, emotion)

        def playingAnim(self, data):
            if self.dialogboxwindow.aniName:
                if data == 0 and not self.playable:
                    self.pos0 = (self.frameGeometry().topLeft().x(), self.frameGeometry().topLeft().y())
                result, self.playable = self.anims[self.dialogboxwindow.aniName].play(data, Pratio=(0.5, 0.5))
                if self.playable:
                    deltaPos=result['position']
                    self.move(self.pos0[0]+deltaPos[0]*self.k, self.pos0[1]+deltaPos[1]*self.k)
                else:
                    self.move(self.pos0[0], self.pos0[1])
        def sizeChange(self, data):
            self.k = data*settings.get('k', 1)#1.1962
            fixedBody=self.image0.resize(tuple(int(x*self.k) for x in self.image0.size)) 
            fixedHalo=self.haloImage.resize(tuple(int(x*self.k) for x in self.haloImage.size))
            self.resize(self.size0[0]*self.k, self.size0[1]*self.k)
            self.halo.setPixmap(ImageQt.toqpixmap(fixedHalo))
            self.halo.setFixedSize(fixedHalo.size[0], fixedHalo.size[1])
            self.halo.move(self.haloPos[0]*self.k, self.haloPos[1]*self.k)

            self.body.setPixmap(ImageQt.toqpixmap(fixedBody))
            self.body.setFixedSize(fixedBody.size[0], fixedBody.size[1])
            self.body.move(0, haloHeight*self.k)

        def mousePressEvent(self, event):
            if self.candialog and event.button() == Qt.LeftButton:
                self.dialog(settings["lobby"])
            if self.candialog and event.button() == Qt.RightButton:
                self.dialog(settings["login"])
            if self.movable and event.button() == Qt.LeftButton:
                self.dragging=True
                self.dragPosition=event.globalPos()-self.frameGeometry().topLeft()
                event.accept()
        def mouseMoveEvent(self, event):
            if self.movable and Qt.LeftButton and self.dragging:
                self.move(event.globalPos()-self.dragPosition)
                event.accept()
        def mouseReleaseEvent(self, event):
            if self.movable and event.button() == Qt.LeftButton:
                self.dragging=False
                self.dialogboxwindow.sizeposChange(self.k / settings.get('k', 1))
                event.accept()
        def keyPressEvent(self, event):
            if event.key() == 69:   #E
                self.settingwindow.show()
        def closeEvent(self, event):
            if not self.closable:
                event.ignore()
            else:
                self.dialogboxwindow.fixedupdate.stop()
                self.fixedupdate.stop()
                self.settingwindow.destroy()
                self.dialogboxwindow.destroy()
                self.dialogboxwindow.voice.stop()
                pg.mixer.music.stop()
                pg.mixer.quit()
                pg.quit()
                QApplication.quit()
        def characterChanged(self, data):
            self.dialogboxwindow.fixedupdate.stop()
            self.fixedupdate.stop()
            self.settingwindow.destroy()
            self.dialogboxwindow.destroy()
            self.dialogboxwindow.voice.stop()
            self.destroy()
            del(self.dialogboxwindow, self.settingwindow, self)
            setCurrentCharacter(data.lower())
            main(name=data.lower())
    class SettingWindow(QDialog):
        def __init__(self):
            super().__init__()
            self.setWindowTitle('Settings')
            self.setGeometry(100, 100, 200, 150)
            #self.setWindowFlags(Qt.Tool)

            self.Emotioncommunicator = Communicator()
            self.Blinkcommunicator = Communicator()
            self.Dialogcommunicator = Communicator()
            self.Movecommunicator = Communicator()
            self.Sizecommunicator = Communicator()
            self.Closecommunicator = Communicator()
            self.Levelcommunicator = Communicator()
            self.VVolumecommunicator = Communicator()
            self.Charactercommunicator = Communicator()

            layout=QVBoxLayout()

            self.emotionCombo = QComboBox()
            self.emotionCombo.addItems(emotions)
            self.emotionCombo.setCurrentIndex(settings['defaultEmotionIndex'])
            layout.addWidget(self.emotionCombo)

            self.blinkCheck = QCheckBox("Blinking eyes", self)
            self.blinkCheck.setChecked(settings['defaultBlinkEyes'])
            layout.addWidget(self.blinkCheck)

            self.dialogCheck = QCheckBox("Dialog", self)
            self.dialogCheck.setChecked(settings['defaultDialog'])
            layout.addWidget(self.dialogCheck)

            moveCheck = QCheckBox("Movable", self)
            moveCheck.setChecked(False)
            layout.addWidget(moveCheck)

            layout.addStretch(1)
            
            sizemessage = QLabel('Size')
            layout.addWidget(sizemessage)

            self.Sslider = QSlider(Qt.Horizontal)
            self.Sslider.setMinimum(1000)
            self.Sslider.setMaximum(30000)
            self.Sslider.setSingleStep(1)
            self.Sslider.setValue(int(k00 *10000))
            layout.addWidget(self.Sslider)

            self.numbox = QLineEdit()
            self.numbox.setText(str(k00))
            layout.addWidget(self.numbox)

            closeCheck = QCheckBox("Closable", self)
            closeCheck.setChecked(True)
            layout.addWidget(closeCheck)

            levelCheck = QCheckBox("Always at the Top Level", self)
            levelCheck.setChecked(False)
            layout.addWidget(levelCheck)

            layout.addStretch(1)
            
            message1 = QLabel('BGM volume')
            layout.addWidget(message1)

            self.Bslider = QSlider(Qt.Horizontal)
            self.Bslider.setMinimum(0)
            self.Bslider.setMaximum(100)
            self.Bslider.setSingleStep(1)
            self.Bslider.setValue(perferences["defaultBGMVolume"]*100)
            layout.addWidget(self.Bslider)
            pg.mixer.music.set_volume(perferences["defaultBGMVolume"])

            message2 = QLabel('Voice volume')
            layout.addWidget(message2)

            self.Vslider = QSlider(Qt.Horizontal)
            self.Vslider.setMinimum(0)
            self.Vslider.setMaximum(100)
            self.Vslider.setSingleStep(1)
            self.Vslider.setValue(perferences["defaultVoiceVolume"]*100)
            layout.addWidget(self.Vslider)

            characterCombo = QComboBox()
            fixedNames=[contrast.get(x, x) if contrast.get(x, x).isupper() else contrast.get(x, x).capitalize() for x in names]
            characterCombo.addItems(fixedNames)
            currentcharacter=getCurrentCharacter()
            characterCombo.setCurrentText(contrast.get(currentcharacter, currentcharacter).capitalize())
            layout.addWidget(characterCombo)

            self.setLayout(layout)
            self.emotionCombo.currentIndexChanged.connect(lambda: self.Emotioncommunicator.data_signal.emit(self.emotionCombo.currentText()))
            self.blinkCheck.stateChanged.connect(lambda state: self.Blinkcommunicator.data_signal.emit(state))
            self.dialogCheck.stateChanged.connect(lambda state: self.Dialogcommunicator.data_signal.emit(state))
            moveCheck.stateChanged.connect(lambda state: self.Movecommunicator.data_signal.emit(state))
            closeCheck.stateChanged.connect(lambda state: self.Closecommunicator.data_signal.emit(state))
            levelCheck.stateChanged.connect(lambda state: self.Levelcommunicator.data_signal.emit(state))

            self.Sslider.valueChanged.connect(self.update_numbox)
            self.numbox.textChanged.connect(self.update_Sslider)

            self.Bslider.valueChanged.connect(lambda value: pg.mixer.music.set_volume(value/100))
            self.Vslider.valueChanged.connect(lambda value: self.VVolumecommunicator.data_signal.emit(value))

            characterCombo.currentIndexChanged.connect(lambda: self.Charactercommunicator.data_signal.emit(names[characterCombo.currentIndex()]))
        def update_numbox(self, value):
            double_value = value / 10000.0
            self.numbox.setText(str(double_value))
            self.Sizecommunicator.data_signal.emit(double_value)

        def update_Sslider(self, value):
            try:
                fvalue=min(max(float(value), 0.1), 3.0)
                int_value = int(fvalue * 10000)
                self.Sslider.setValue(int_value)
                self.numbox.setText(str(fvalue))
                self.Sizecommunicator.data_signal.emit(fvalue)
            except ValueError:
                pass

    class DialogBoxWindow(QWidget):
        def __init__(self, dialogBoxImages):
            super().__init__()
            self.k=k00
            self.dialogBoxImages=dialogBoxImages
            self.voiceVolume=perferences["defaultVoiceVolume"]
            self.timeCommunicator=Communicator()
            self.aniName=None

            layout=QVBoxLayout()
            # 设置无边框和透明背景
            self.setWindowModality(Qt.NonModal)
            self.setWindowFlags(Qt.FramelessWindowHint|Qt.ToolTip)
            self.setAttribute(Qt.WA_TranslucentBackground, True)
            self.setGeometry(settings["dialogBoxPos"][0]*self.k/1.1962, settings["dialogBoxPos"][1]*self.k/1.1962, 1, 1)
            self.boxlabel=QLabel(self)
            self.boxlabel.setGeometry(0, 0, 1, 1)
            layout.addWidget(self.boxlabel)

            self.textlabel=QLabel(self)
            self.textlabel.setGeometry(0, 0, 1, 1)
            layout.addWidget(self.textlabel)
        def vvolumeChanged(self, data):
            self.voiceVolume=data/100
        def showDB(self, indexes, emotions, order=0):
            self.indexes=indexes
            self.emotions=emotions
            self.order=order
            index=self.indexes[self.order]
            if '|' in index:
                index, self.aniName = index.split('|')
            else:
                self.aniName = None
            self.emotion=self.emotions[self.order]
            self.dialogBox0=self.dialogBoxImages[index][0]
            dialogBox=self.dialogBox0.resize(tuple(int(x*self.k/1.1962) for x in self.dialogBox0.size))
            self.dialogText0=self.dialogBoxImages[index][1]
            dialogText=self.dialogText0.resize(tuple(int(x*self.k/1.1962) for x in self.dialogText0.size))
            PdialogBox=ImageQt.toqpixmap(dialogBox)
            PdialogText=ImageQt.toqpixmap(dialogText)
            self.order += 1
            if self.order == len(self.indexes):
                self.end=True
            else:
                self.end=False
            self.boxlabel.setPixmap(PdialogBox)
            self.boxlabel.setGeometry(0, 0, dialogBox.width, dialogBox.height)
            self.textlabel.setPixmap(PdialogText)
            self.textlabel.setGeometry(0, 0, dialogText.width, dialogText.height)
            if self.order == 1:
                setopacity(self.boxlabel, 0)
                setopacity(self.textlabel, 0)

            self.dialoging=self.emotionchange=True
            self.t0=0
            pg.mixer.stop()
            try:
                namefile=name if name.isupper() else name.capitalize()
                self.voice = pg.mixer.Sound(f"audios/JP_{namefile}/{name}_{index}.ogg")
            except:
                self.voice = pg.mixer.Sound("audios/mute.ogg")
            self.voice.set_volume(self.voiceVolume)
            self.length=max(self.voice.get_length(), 1)
            self.fixedupdate = QTimer(self)
            self.fixedupdate.timeout.connect(self.frameUpdate)
            self.voice.play()
            #self.hide()
            self.show()
            self.fixedupdate.start(1000/30)
        def frameUpdate(self, fadeIn=0.6, fadeOut=0.6):
            self.voice.set_volume(self.voiceVolume)
            if self.t0 == 0:
                self.t0 = time.time()
                t=0
                self.sizeposChange(self.k)
                self.tempCanblink=imagewindow.canblink
                imagewindow.canblink=False
                imagewindow.update(self.emotion)
            else:
                t = time.time()-self.t0
            if self.dialoging and imagewindow.candialog:
                self.timeCommunicator.data_signal.emit(t)
                if 0 <= t and t <= fadeIn:
                    if self.order == 1:
                        setopacity(self.boxlabel, t/fadeIn)
                    else:
                        setopacity(self.boxlabel, 1)
                    setopacity(self.textlabel, t/fadeIn)
                elif fadeIn < t and t <= self.length:
                    setopacity(self.boxlabel, 1)
                    setopacity(self.textlabel, 1)
                elif self.length < t and t <= self.length+fadeOut:
                    if self.emotionchange and self.end:
                        imagewindow.update(emotions[settings['defaultEmotionIndex']])
                        imagewindow.canblink=self.tempCanblink
                        self.emotionchange=False
                    if self.end:
                        setopacity(self.boxlabel, (self.length+fadeOut - t)/fadeOut)
                    else:
                        setopacity(self.boxlabel, 1)
                    setopacity(self.textlabel, (self.length+fadeOut - t)/fadeOut)
                else:
                    setopacity(self.boxlabel, 0)
                    setopacity(self.textlabel, 0)
                    t = self.length+fadeOut+1
                    self.hide()
                    self.dialoging=False
            elif not self.end:
                self.showDB(self.indexes, self.emotions, self.order)
            elif self.emotionchange:
                self.voice.stop()
                self.hide()
                setopacity(self.boxlabel, 0)
                setopacity(self.textlabel, 0)
                imagewindow.update(emotions[settings['defaultEmotionIndex']])
                imagewindow.canblink=self.tempCanblink
                self.emotionchange=self.dialoging=False
        def sizeposChange(self, data):
            self.k=data
            dialogBox=self.dialogBox0.resize(tuple(int(x*self.k/1.1962) for x in self.dialogBox0.size))
            dialogText=self.dialogText0.resize(tuple(int(x*self.k/1.1962) for x in self.dialogText0.size))
            PdialogBox=ImageQt.toqpixmap(dialogBox)
            PdialogText=ImageQt.toqpixmap(dialogText)
            self.boxlabel.setPixmap(PdialogBox)
            self.textlabel.setPixmap(PdialogText)

            self.boxlabel.setFixedSize(dialogBox.width, dialogBox.height)
            self.textlabel.setFixedSize(dialogText.width, dialogText.height)

            charactercenter=imagewindow.frameGeometry().center()
            self.setGeometry(charactercenter.x()+(settings["dialogBoxPos"][0]-settings['characterPos'][0])*self.k/1.1962-imagewindow.size0[0]/2*imagewindow.k,
                    charactercenter.y()+(settings["dialogBoxPos"][1]-settings['characterPos'][1])*self.k/1.1962-imagewindow.size0[1]/2*imagewindow.k, 
                    dialogBox.width, dialogBox.height)
        def closeEvent(self, event):
            event.ignore()
        
    imagewindow = ImageWindow()
    imagewindow.show()
    signal.signal(signal.SIGINT, lambda: imagewindow.signalReceived())
    if firstTime:
        pg.mixer.music.load("audios/theme_14.ogg")
        pg.mixer.music.play(-1)

if __name__ == "__main__":
    if screen.width()/1600 != screen.height()/900:
        msg=QMessageBox.question(None, "提示", "屏幕比例不符合16:9，角色初始位置会歪，是否继续?", QMessageBox.Yes|QMessageBox.No)
        if msg == QMessageBox.Yes:
            main(getCurrentCharacter(), firstTime=True)
            sys.exit(app.exec_())
    else:
        main(getCurrentCharacter(), firstTime=True)
        sys.exit(app.exec_())
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtWidgets import QLabel, QVBoxLayout, QMainWindow
import time
import pygame.mixer as mixer
from random import randrange
from math import sin

from windows.settings_window import SettingsWindow
from windows.dialogbox_window import DialogBoxWindow
from getResources import GLOBAL_CONFIG, global_variables
from renderDialogBox import *
from windows.UI_hide_desktop_icons_button_window import UI_HideDesktopIconsButtonWindow
from windows.functions import get_fps, convert_PIL_pictures_to_QPixmap
from signal_bus import signal_bus
from dataclasses_ import CharacterConfig, SettingsParameters
from animation.pyside_animation_player import PysideAnimationPlayer

class ImageWindow(QMainWindow):

    anim_signal = Signal(dict)

    def __init__(self, character_config: CharacterConfig):
        super().__init__()
        self.character_config = character_config
        self.settings_parameters = SettingsParameters(
            emotion=self.character_config.emotions[self.character_config.settings['defaultEmotionIndex']],
            blink=self.character_config.settings['defaultBlinkEyes'],
            dialog=self.character_config.settings['defaultDialog'],
            size=self.character_config.k0,
            voice_volume=GLOBAL_CONFIG.PREFERENCES["defaultVoiceVolume"]
        )

        self.layout = QVBoxLayout()
        # 设置无边框和透明背景
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        self.haloPos = character_config.settings['halo']
        self.t = 0

        self.playable = False

        self.character_config.pictures = convert_PIL_pictures_to_QPixmap(self.character_config.pictures)

        self.image0 = self.character_config.pictures[self.settings_parameters.emotion]
        self.haloImageP = self.character_config.pictures['halo']

        self.halo = QLabel('halo', self)
        self.halo.setPixmap(self.haloImageP)
        self.halo.setFixedSize(self.haloImageP.width(), self.haloImageP.height())
        self.halo.move(self.haloPos[0], self.haloPos[1])
        self.layout.addWidget(self.halo)
        self.size0 = (self.image0.width(), self.image0.height() + self.character_config.halo_height)
        self.resize(self.size0[0], self.size0[1])

        self.body = QLabel('body', self)
        self.body.setPixmap(self.image0)
        self.body.setFixedSize(self.image0.width(), self.image0.height())
        self.body.move((self.width() - self.image0.width()) / 2,
                       (self.height() - self.image0.height() + self.character_config.halo_height) / 2)
        self.layout.addWidget(self.body)
        self.setLayout(self.layout)

        self.move(self.character_config.settings['characterPos'][0] * GLOBAL_CONFIG.k00 / GLOBAL_CONFIG.ZOOM_SCALE,
                  self.character_config.settings['characterPos'][1] * GLOBAL_CONFIG.k00 / GLOBAL_CONFIG.ZOOM_SCALE)
        self.sizeChange(GLOBAL_CONFIG.k00)

        self.fps = get_fps()

        self.fixedupdate = QTimer(self)
        self.fixedupdate.timeout.connect(self.frameUpdate)
        self.posHistory = []
        self.t0 = 0
        self.fixedupdate.start(1000 / GLOBAL_CONFIG.PREFERENCES['maxFPS'])

        self.dialogboxwindow = DialogBoxWindow(self.character_config.name, self.character_config.dialogBoxImages,
                                               self.character_config.emotions, self.character_config.settings,
                                               GLOBAL_CONFIG.k00, self)
        self.dialogboxwindow.show()

        if True:
            from windows.UI_input_window import UI_InputWindow_classic

            self.UI_InputWindow = UI_InputWindow_classic()
        if GLOBAL_CONFIG.PREFERENCES["fastCloseButton"]:
            from windows.UI_fast_close_button_window import UI_FastCloseButtonWindow
            self.UI_fastCloseButtonWindow = UI_FastCloseButtonWindow()
            self.UI_fastCloseButtonWindow.show()

        screen = QApplication.primaryScreen()
        self.UI_hideDesktopIconsButtonWindow = UI_HideDesktopIconsButtonWindow(
            (screen.size().width(), screen.size().height()))
        self.UI_hideDesktopIconsButtonWindow.show()
        # self.UI_ChangeCharacterModeButtonWindow = UI_ChangeCharacterModeButtonWindow((screen.size().width(), screen.size().height()))
        # self.UI_ChangeCharacterModeButtonWindow.show()

        self.settingwindow = SettingsWindow(
            GLOBAL_CONFIG.CONTRAST.get(self.character_config.name, self.character_config.name),
            self.character_config.emotions, self.character_config.settings, GLOBAL_CONFIG.k00)

        signal_bus.settings_signal.connect(self.settings_signal_received)
        signal_bus.close_signal.connect(lambda: self.closeEvent(None))
        signal_bus.dialog_anim_signal.connect(self.play_anim)
        signal_bus.AI_dialog_input_signal.connect(self.start_AI_generate)

        if self.settings_parameters.dialog:
            self.judgeEnterDialog()
        signal_bus.AI_generate_get_signal.connect(self.AI_generate)
        self.AI_firsttime = True
        self.canInput = True

        if self.character_config.firstTime:
            mixer.music.set_volume(GLOBAL_CONFIG.PREFERENCES["defaultBGMVolume"])
            signal_bus.debug_show_signal.emit(True)

    def functions_init(self, character_changed, init_AI):
        self.func_character_changed = character_changed
        self.func_init_AI = init_AI

    ######################################
    # 信号槽函数
    def settings_signal_received(self, key, value):
        if hasattr(self.settings_parameters, key):
            setattr(self.settings_parameters, key, value)
        if key == 'emotion':
            self.update(value)
        elif key == 'move':
            self.settingwindow.dialogCheck.setChecked(not self.settings_parameters.move)
            self.settingwindow.dialogCheck.setCheckable(not self.settings_parameters.move)
        elif key == 'size_preview' or key == 'size_final':
            setattr(self.settings_parameters, 'size', value)

            precise = False if key == 'size_preview' else True
            self.sizeChange(self.settings_parameters.size, precise=precise)
            self.dialogboxwindow.sizeposChange(
                self.settings_parameters.size / self.character_config.settings.get('k', 1))
            
        elif key == 'top_level':
            if value:  # True
                # 将窗口置于顶层
                self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
                self.dialogboxwindow.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnTopHint)
                self.show()
            else:
                self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)
                self.dialogboxwindow.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)
                self.show()

        elif key == 'bgm_volume':
            from pygame import mixer
            mixer.music.set_volume(value)
        elif key == 'voice_volume':
            self.dialogboxwindow.voiceVolume = value
        elif key == 'AI_open_new_topic' and global_variables.current_AI:
            global_variables.current_AI.b = True

        elif key == 'AI_save_state' and global_variables.current_AI:
            global_variables.current_AI.save = value
        elif key == 'character':
            self.characterChanged(value)

        elif key == 'text':  # value: Dict['content_list': List[str], 'emotion': str]
            self.AI_generate(value)

        # Custom
        elif key == 'terminate':
            signal_bus.close_signal.emit()
    def UI_windows_signal_received(self, key, value):
        if key == "close":
            self.hide()


    ######################################

    def update(self, data, changeCurrentEmotion=True):
        """emotion改变时运行"""
        # if changeCurrentEmotion:
        #    signal_bus.settings_signal.emit('emotion', data)
        if not data:
            data = self.character_config.emotions[0]
        self.image0 = self.character_config.pictures[data]
        self.image1 = self.image0.scaled(
            *(int(x * self.settings_parameters.size) for x in (self.image0.width(), self.image0.height())),
            Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.body.setPixmap(self.image1)

    def frameUpdate(self):
        """每帧运行一次"""
        blinkingtime = self.character_config.settings['blinkingTime']
        deltablinktime = self.character_config.settings['deltaBlinkTime']

        if self.t0 == 0:
            self.t0 = time.time()
            self.sblinktime = 0
        t = time.time() - self.t0
        dy = sin(t / 2) * 5 * self.settings_parameters.size / GLOBAL_CONFIG.ZOOM_SCALE
        self.halo.move(self.haloPos[0] * self.settings_parameters.size,
                       self.haloPos[1] * self.settings_parameters.size + dy)
        if self.settings_parameters.blink:
            if t - self.sblinktime > blinkingtime:
                self.update(self.settings_parameters.emotion)
                self.sblinktime = t + blinkingtime + 999999
            if t % deltablinktime < 1 / GLOBAL_CONFIG.PREFERENCES['maxFPS'] or t % deltablinktime > deltablinktime - 1 / \
                    GLOBAL_CONFIG.PREFERENCES['maxFPS']:
                self.update("eyeclose", changeCurrentEmotion=False)
                self.sblinktime = t

        currentpos = (self.pos().x(), self.pos().y())
        self.posHistory.append(currentpos)
        if any(x == 0 for x in currentpos):
            if not (self.posHistory[0] != self.posHistory[0] and self.posHistory[0] != self.posHistory[0]):
                self.move(*self.posHistory[1])
        if len(self.posHistory) > 3:
            self.posHistory.pop(0)

        # print(self.fps())

    #废弃函数
    def signalReceived(self, message):
        """接收到socket信号时的反应"""

        signal_bus.settings_signal.emit('dialog', False)
        signal_bus.settings_signal.emit('blink', False)

        indexType = {'fail': "emotionWhenFailingIndex"}[message]
        try:
            self.settingwindow.dialogCheck.setChecked(False)
            self.settingwindow.blinkCheck.setChecked(False)
            if indexType in self.character_config.settings.keys():
                self.settingwindow.emotionCombo.setCurrentIndex(self.character_config.settings[indexType])
        except Exception as e:
            print(f"[ERROR]Socket Received Error: {e}")
        self.update(self.character_config.emotions[self.character_config.settings[
            indexType]] if indexType in self.character_config.settings.keys() else self.settings_parameters.emotion)

        try:
            namefile = self.character_config.name if self.character_config.name.isupper() else self.character_config.name.capitalize()
            voice = mixer.Sound(f"audios/JP_{namefile}/{self.character_config.name}_battle_retire.ogg")
        except:
            voice = mixer.Sound("audios/mute.ogg")
        voice.set_volume(self.settings_parameters.voice_volume)
        voice.play()

    ######################################
    # AI函数

    def start_AI_generate(self, data: str):
        if self.AI_firsttime:
            global_variables.AI_thread.start()
            self.AI_firsttime = False
        exap = list(self.character_config.dialogBoxContent.values())[0]
        emo = next((s for s in self.character_config.emotions if s.startswith(exap[1])), None).split('_')[-1]
        example = ''.join(exap[0]) + '#' + emo + '#'
        signal_bus.AI_generate_send_signal.emit({'current_character': GLOBAL_CONFIG.CONTRAST.get(
            self.character_config.name.upper(), self.character_config.name), 'user_content': data, 'example': example})

    def AI_generate(self, data: dict):
        content_list, emotion = data['content_list'], data['emotion']
        emotion = [next((s for s in self.character_config.emotions if s.endswith(emotion)), None)]
        if not emotion:
            emotion = self.character_config.emotions[0]
        custom_dialogbox = render_Lobby_balloon(content_list)
        content = ''.join(content_list)
        self.dialogboxwindow.showDB([content], emotion, custom=True, custom_dialogboxs=[custom_dialogbox],
                                    lasting_time=len(content) * 0.2)
        self.canInput = True

    ######################################

    def dialog(self, indexes):
        index = indexes[randrange(0, len(indexes))]
        emotion = [next((s for s in self.character_config.emotions if
                         s.startswith(self.character_config.dialogBoxContent[inde.split('|')[0]][1])), None) for inde in
                   index]
        self.dialogboxwindow.showDB(index, emotion)

    def judgeEnterDialog(self):
        if self.character_config.today_is_birthday_sensei and "birthday_player" in self.character_config.settings.keys():
            self.dialog(self.character_config.settings["birthday_player"])
        else:
            self.dialog(self.character_config.settings["login"])


    def anim_signal_received(self, dic):
        position = dic.get('position', (0, 0))
        self.move(*[int(x - y) for x, y in zip(self.position0, position)])

    def play_anim(self, anim_name):
        """角色动画系统"""
        self.position0 = (self.pos().x(), self.pos().y())

        self.anim_signal.connect(self.anim_signal_received)
        self.animation_player = PysideAnimationPlayer(self.anim_signal, anim_name, stop_time=None, Pratio=(0.5, 0.5))
        self.animation_player.play()


    def sizeChange(self, data, precise=True):
        self.settings_parameters.size = data * self.character_config.settings.get('k', 1)  # GLOBAL_CONFIG.ZOOM_SCALE
        
        if precise:
            # 高质量插值处理 - 使用ImageQt的转换函数
            from PIL import Image
            from functions.ImageQt import fromqimage, toqpixmap
            
            # 直接使用ImageQt的fromqimage函数转换QImage到PIL Image
            body_pil = fromqimage(self.image0.toImage())
            halo_pil = fromqimage(self.haloImageP.toImage())
            
            # 使用LANCZOS高质量插值缩放
            target_body_size = (
                max(1, int(body_pil.width * self.settings_parameters.size)),
                max(1, int(body_pil.height * self.settings_parameters.size))
            )
            target_halo_size = (
                max(1, int(halo_pil.width * self.settings_parameters.size)),
                max(1, int(halo_pil.height * self.settings_parameters.size))
            )
            
            resized_body = body_pil.resize(target_body_size, Image.Resampling.LANCZOS)
            resized_halo = halo_pil.resize(target_halo_size, Image.Resampling.LANCZOS)
            
            # 转换回QPixmap
            fixedBody = toqpixmap(resized_body)
            fixedHalo = toqpixmap(resized_halo)
        else:
            # 快速预览缩放 - 使用Qt原生方法
            fixedBody = self.image0.scaled(
                *(int(x * self.settings_parameters.size) for x in (self.image0.width(), self.image0.height())),
                Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation)
            fixedHalo = self.haloImageP.scaled(
                *(int(x * self.settings_parameters.size) for x in (self.haloImageP.width(), self.haloImageP.height())),
                Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation)
        
        self.resize(self.size0[0] * self.settings_parameters.size, self.size0[1] * self.settings_parameters.size)
        self.halo.setPixmap(fixedHalo)
        self.halo.setFixedSize(fixedHalo.width(), fixedHalo.height())
        self.halo.move(self.haloPos[0] * self.settings_parameters.size, self.haloPos[1] * self.settings_parameters.size)

        self.body.setPixmap(fixedBody)
        self.body.setFixedSize(fixedBody.width(), fixedBody.height())
        self.body.move(0, self.character_config.halo_height * self.settings_parameters.size)

    ######################################
    # 事件函数

    def mousePressEvent(self, event):
        if self.settings_parameters.dialog and event.button() == Qt.LeftButton:
            self.dialog(self.character_config.settings["lobby"])
        if self.settings_parameters.dialog and event.button() == Qt.RightButton:
            self.judgeEnterDialog()
        if self.settings_parameters.move and event.button() == Qt.LeftButton:
            self.dragging = True
            self.dragPosition = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.settings_parameters.move and Qt.LeftButton and self.dragging:
            self.move(event.globalPos() - self.dragPosition)
            event.accept()

    def mouseReleaseEvent(self, event):
        if self.settings_parameters.move and event.button() == Qt.LeftButton:
            self.dragging = False
            self.dialogboxwindow.sizeposChange(
                self.settings_parameters.size / self.character_config.settings.get('k', 1))
            event.accept()

    def keyPressEvent(self, event):
        if event.key() == 69:  # E
            self.settingwindow.show()
        elif event.key() == 67 and self.canInput and global_variables.current_AI:  # C
            self.UI_InputWindow.show()
            self.canInput = False

    def closeEvent(self, event):
        if event and not self.settings_parameters.close:
            event.ignore()
        else:
            self.hide()
            self.dialogboxwindow.fixedupdate.stop()
            self.fixedupdate.stop()
            self.settingwindow.close()
            self.dialogboxwindow.close()
            self.dialogboxwindow.voice.stop()
            if not event:
                mixer.music.stop()
                mixer.quit()
                global_variables.socket_thread.running = False
                global_variables.socket_thread.quit()
                global_variables.socket_thread.wait(100)
                QApplication.quit()

    ######################################

    def characterChanged(self, character_name):
        self.dialogboxwindow.fixedupdate.stop()
        self.fixedupdate.stop()
        self.settingwindow.hide()
        self.settingwindow.deleteLater()
        self.dialogboxwindow.voice.stop()
        self.dialogboxwindow.hide()
        self.dialogboxwindow.deleteLater()
        self.hide()
        self.deleteLater()

        self.func_character_changed(character_name.lower())
        del (self.dialogboxwindow, self.settingwindow, self)

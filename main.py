from multiprocessing import Process, current_process, freeze_support
import sys

if getattr(sys, 'frozen', False):
    freeze_support()
    
if current_process().name == 'MainProcess' and __name__ == '__main__':
    from actions_brfore_start import ask_if_start
    from PySide6.QtWidgets import QApplication
    from PySide6.QtGui import QGuiApplication

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)

    screens = QGuiApplication.screens()
    screen = screens[0]

    if ask_if_start(screen):
        from loadingWindow.loading import LoadingWindowControl

        LoadingWindowControl.createLoadingWindow()
        from windows.image_window import ImageWindow, CharacterConfig
        from PySide6.QtCore import QThread

        import signal
        import os

        from getResources import GLOBAL_CONFIG, global_variables, getCurrentCharacter, getDialogBoxContent, loadFont, setCurrentCharacter
        from resource_loader import getCharacterInf
        from renderDialogBox import *
        from animation.animation_player import AnimationPlayer
        from windows.background_window import load_background_window
        from signal_bus import signal_bus
        from AI.AI_control import AI

        default_font = app.font()

        if GLOBAL_CONFIG.PREFERENCES["debugWindow"]:
            from windows.debug_window import DebugWindow
            debug_window = DebugWindow(default_font)

        LoadingWindowControl.messageLoadingWindow("Module import completed.")

        overFont = loadFont(*GLOBAL_CONFIG.PREFERENCES["font"])
        if overFont:
            app.setFont(overFont)

        LoadingWindowControl.messageLoadingWindow("Font loading completed.")

        if GLOBAL_CONFIG.PREFERENCES["defaultOverallCharacterSize"]:
            GLOBAL_CONFIG.k00 = GLOBAL_CONFIG.PREFERENCES["defaultOverallCharacterSize"]
        else:
            GLOBAL_CONFIG.k00 = round(
                min(screen.geometry().width() / 1600, screen.geometry().height() / 900) * GLOBAL_CONFIG.ZOOM_SCALE, 3)

        anims = {}
        for animName in GLOBAL_CONFIG.PREFERENCES['animNames']:
            anims[animName] = AnimationPlayer(os.path.join('AnimationClip', animName + '.anim'))
            LoadingWindowControl.messageLoadingWindow(f"Animation:{animName}")
        GLOBAL_CONFIG.ANIMS = anims
        LoadingWindowControl.messageLoadingWindow("Animation initialization completed.")
        current_AI = AI_thread = None


        def init_AI(AI_name, inf_dict):
            if not GLOBAL_CONFIG.PREFERENCES["defaultInitAI"] or AI_name in GLOBAL_CONFIG.AI_SAVES:
                try:
                    if not global_variables.current_AI:
                        global_variables.current_AI = AI(AI_name, inf_dict)
                        global_variables.AI_thread = QThread()
                        global_variables.current_AI.moveToThread(global_variables.AI_thread)
                    else:
                        global_variables.AI_thread.quit()
                        global_variables.AI_thread.wait()
                        global_variables.current_AI = AI(AI_name, inf_dict)
                        global_variables.AI_thread = QThread()
                        global_variables.current_AI.moveToThread(AI_thread)
                except Exception as e:
                    print(f"[ERROR]AI Error: {e}")

        signal_bus.AI_start_signal.connect(init_AI)


        def mainChar(name, firstTime=False):
            LoadingWindowControl.messageLoadingWindow("Start loading character...")
            pictures, settings = getCharacterInf(name)
            LoadingWindowControl.messageLoadingWindow("Character loading completed.")
            haloHeight = settings.get('haloHeight', 100)
            emotions = list(pictures.keys())
            emotions.remove('halo')
            k0 = settings.get('k', 1) * GLOBAL_CONFIG.k00
            dialogBoxContent = getDialogBoxContent(name)
            dialogBoxImages = {}
            for key, content in dialogBoxContent.items():
                dialogBoxX, dialogTextX = render_Lobby_balloon(content[0])
                dialogBoxImages[key] = [dialogBoxX.resize(
                    tuple(int(x * GLOBAL_CONFIG.k00 / GLOBAL_CONFIG.ZOOM_SCALE) for x in dialogBoxX.size)),
                                        dialogTextX.resize(tuple(
                                            int(x * GLOBAL_CONFIG.k00 / GLOBAL_CONFIG.ZOOM_SCALE) for x in
                                            dialogTextX.size)), content[1]]
                LoadingWindowControl.messageLoadingWindow(f"Dialog:{key}")
            LoadingWindowControl.messageLoadingWindow("Dialog box rendering completed.")
            if firstTime:
                LoadingWindowControl.messageLoadingWindow("complete")
                global today_is_birthday_sensei
                from functions.birthday import getIftodayIsSenseiBirthday
                today_is_birthday_sensei = getIftodayIsSenseiBirthday(app, screen)

            character_config = CharacterConfig(name,
                                               k0,
                                               pictures,
                                               settings,
                                               emotions,
                                               haloHeight,
                                               dialogBoxImages,
                                               dialogBoxContent,
                                               firstTime,
                                               today_is_birthday_sensei,
                                               screen
                                               )
            imagewindow = ImageWindow(character_config)
            imagewindow.functions_init(character_changed, init_AI)
            imagewindow.show()
            signal.signal(signal.SIGINT, lambda: imagewindow.signalReceived())
            if firstTime:
                from audios.sound import play_background_music
                play_background_music("audios/theme_14.ogg")


        def character_changed(name):
            setCurrentCharacter(name)
            mainChar(name=name)


        def process_loading():
            background_window_process = Process(target=load_background_window,
                                                args=(GLOBAL_CONFIG.PREFERENCES.get("dynamicBackgroundOffset", (0, 0)),))
            background_window_process.daemon = True
            background_window_process.start()

            from job_object import assign_process_to_job
            assign_process_to_job(GLOBAL_CONFIG.JOB_OBJECT, background_window_process)

        if GLOBAL_CONFIG.PREFERENCES["dynamicBackground"]:
            process_loading()
        
        try:
            from socket_ import SocketListener
            socketThread = SocketListener(signal_bus.settings_signal)
            socketThread.start()
            global_variables.socket_thread = socketThread
        except Exception as e:
            print(f"[ERROR]Create Socket Error: {e}")
            global_variables.socketThread = None
            
        mainChar(getCurrentCharacter(), firstTime=True)
        sys.exit(app.exec())

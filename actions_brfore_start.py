def ask_if_start(screen):
    from getResources import GLOBAL_CONFIG
    from PySide6.QtWidgets import QMessageBox
    
    if GLOBAL_CONFIG.PREFERENCES["repeatConfirm"] != 0:
        from windows.repeat_confirm_window import repeat_confirm
        if repeat_confirm(GLOBAL_CONFIG.PREFERENCES["repeatConfirm"]):
            ###
            if screen.geometry().width()/1600 != screen.geometry().height()/900:
                print(f"[DEBUG]Screen Size: {screen.geometry().width(),screen.geometry().height()}")
                msg=QMessageBox.warning(None, "提示", "屏幕比例不符合16:9，角色初始位置会歪，是否继续?", QMessageBox.Yes|QMessageBox.No)
                if msg == QMessageBox.Yes:
                    return True
    else:
        return True
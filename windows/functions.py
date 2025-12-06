import time
from typing import Dict

def get_fps(default_fps = 60):
    t = None
    def fps():
        nonlocal t
        if t:
            t0 = t
            t = time.time()
            return 1/(t - t0+0.000000001)
        else:
            t = time.time()
            return default_fps
    return fps

def convert_PIL_pictures_to_QPixmap(pictures: Dict):
    """把pillow的图片字典转换成QPixmap"""
    from functions import ImageQt
    return {x[0]: ImageQt.toqpixmap(x[1]) for x in pictures.items()}

def setopacity(label, opacity):
    """
    设置标签透明度
    """
    from PySide6.QtWidgets import QGraphicsOpacityEffect

    # 先移除旧 effect，避免重复添加
    if label.graphicsEffect():
        label.graphicsEffect().deleteLater()

    effect = QGraphicsOpacityEffect()
    label.setGraphicsEffect(effect)
    effect.setOpacity(opacity)

    # 👇 关键：将 effect 存为 label 的属性，防止被回收！
    label._opacity_effect = effect  # 保持引用


def verifyDate(date_str):
    """
    验证日期是否合法
    """
    import time
    try:
        # 将MMDDYYYY转换为MM/DD/YYYY格式以便strptime解析
        formatted_date = f"{date_str[:2]}/{date_str[2:4]}/{date_str[4:]}"
        t=time.strptime(formatted_date, "%m/%d/%Y")
        return True
    except ValueError:
        return False


def hideDesktopIcons(*args):
    """隐藏和显示桌面图标"""
    import ctypes
    import time

    user32 = ctypes.windll.user32
    try:
            # 1. 找到 Progman
        progman = user32.FindWindowW("Progman", None)
        if not progman:
            print("[ERROR]No Progman Found")
            return

        # 2. 发送 0x52C 消息，触发 WorkerW 创建（关键！）
        user32.SendMessageW(progman, 0x52C, 0, 0)

        workerw = None

        # 3. 枚举所有 WorkerW
        while True:
            workerw = user32.FindWindowExW(None, workerw, "WorkerW", None)
            if not workerw:
                break

            # 4. 在每个 WorkerW 下查找 SHELLDLL_DefView（用于判断是否是正确容器）
            defview = user32.FindWindowExW(workerw, None, "SHELLDLL_DefView", None)
            if defview:
                # 5. 在 SHELLDLL_DefView 下查找 SysListView32（真正的图标窗口）
                listview = user32.FindWindowExW(defview, None, "SysListView32", None)
                if listview:
                    # 找到了！隐藏或显示
                    user32.ShowWindow(listview, 0 if args[0] == 1 else 5)
                    break

        # 6. 隐藏/显示任务栏
        tray = user32.FindWindowW("Shell_TrayWnd", None)
        if tray:
            user32.ShowWindow(tray, 0 if args[0] == 1 else 5)
    except Exception as e:
        print("[ERROR]Hiding Failed: {e}")
    time.sleep(0.3)


from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QLabel, QVBoxLayout
from custom_QDialog import CustomQDialog as QDialog
from PySide6.QtGui import QGuiApplication
from functions.set_background_layer import set_background_layer

from PySide6.QtWidgets import QMainWindow, QLabel, QVBoxLayout
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import Qt, QUrl
# 导入刚才生成的资源文件

from PySide6.QtWebEngineCore import QWebEnginePage

class JSConsoleLogger(QWebEnginePage):
    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
        # level: 日志级别 (0=LOG, 1=WARN, 2=ERROR)
        #level_names = ["LOG", "WARN", "ERROR"]
        #prefix = f"JS [{level_names[level]}] (Line {lineNumber}): "
        
        # 打印到 Python 控制台
        print(level, message, lineNumber)
        
        # 如果你想把错误也显示在窗口状态栏，可以在这里添加逻辑
        # self.parent().statusBar().showMessage(message, 3000)


class BackgroundWindow(QMainWindow):
    def __init__(self, app, offset):
        super().__init__()
        self.app = app
        self.offset = offset
        self.screen = QGuiApplication.primaryScreen()

        self.title = "Desktop Lobby Background"
        self.setWindowTitle(self.title)
        # 设置无边框和透明背景
        #self.setWindowFlags(Qt.FramelessWindowHint)
        #self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint)
        self.setStyleSheet("QDialog{background-color: black;}")
        screen_g = self.screen.geometry()
        self.screen_size = (screen_g.width(), screen_g.height())

        # 创建 WebEngineView
        self.web_view = QWebEngineView()

        # 1. 创建自定义的 Page 对象并设置给 View
        logger_page = JSConsoleLogger(self.web_view)
        self.web_view.setPage(logger_page)
        
        self.setCentralWidget(self.web_view)

        name = 'CH9997_home'
        # 3. 构建 HTML 内容 (直接拼接或读取文件)
        html_content = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body, html {
            overflow: hidden;
            margin: 0;
            padding: 0;

            pointer-events: none;
            background-color: transparent;
        }

    </style>
</head>
""" f"""
<body>

    <!-- 2. Spine 容器 -->
    <div id="spine-container">
    <spine-skeleton 
        id="player" 
        atlas="../lobbies/{name}/{name}.atlas"
        skeleton="../lobbies/{name}/{name}.skel"
        animations="[0, Idle_01, true]"

        style="width: {self.screen_size[0]}px; height: {self.screen_size[1]}px; display: block;">
    </spine-skeleton>
    </div>

    <!-- 3. 调试脚本：监听错误 -->
    <script src="../spine-webcomponents.js"></script>
</body>
</html>
"""

        # 4. 加载 HTML
        # 使用 self.web_view.setHtml(html, base_url) 可以解决相对路径问题
        # 这里的 base_url 指向资源前缀，这样如果 html 里引用了相对路径的图片也能找到
        base_url = QUrl("file://")
        self.web_view.setHtml(html_content, base_url)

        self.show()
        self.lower()
        
        QTimer.singleShot(100, self.set_pos)
        QTimer.singleShot(200, self.set_background_layer)
    def set_background_layer(self):
        set_background_layer(self.title)
    def set_pos(self):
        border_width_physical = self.get_border_width()
        offset_x, offset_y = self.offset
        self.setGeometry(-border_width_physical-offset_x, -border_width_physical-offset_y, *self.screen_size)
    def get_border_width(self):
        """获取窗口边框宽度（物理像素）"""
        frame_rect = self.frameGeometry()  # 包含边框的物理矩形
        client_rect = self.geometry()       # 客户区逻辑矩形

        # 计算左右边框总宽度（逻辑像素）
        border_width_logical = frame_rect.width() - client_rect.width()

        # 转换为物理像素（考虑 DPI 缩放）
        dpi_x = self.screen.physicalDotsPerInchX()
        dpi_y = self.screen.physicalDotsPerInchY()
        # Qt 的逻辑像素到物理像素的缩放因子
        scale_factor = dpi_x / 96.0  # 96 是 Qt 的默认 DPI
        border_width_physical = int(border_width_logical * scale_factor)

        return border_width_physical

def load_background_window(offset):
    from PySide6.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)
    c=BackgroundWindow(app, offset)
    sys.exit(app.exec_())


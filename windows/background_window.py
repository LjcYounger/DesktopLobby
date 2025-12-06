from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QLabel, QVBoxLayout
from custom_QDialog import CustomQDialog as QDialog
from PySide6.QtGui import QPixmap, QGuiApplication
from functions.set_background_layer import set_background_layer
class BackgroundWindow(QDialog):
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

        self.p_images = {}
        front_image = QPixmap('images/BG_MainOffice-16_9').scaled(*self.screen_size, Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation)
        cloud_image = QPixmap('images/Lobby/Bg_Public_Cloud.png')
        self.p_images ['main_office'] = front_image
        self.p_images ['cloud'] = cloud_image
        layout = QVBoxLayout()

        self.main_office = QLabel()
        self.main_office.setPixmap(self.p_images['main_office'])
        self.main_office.setGeometry(0, 0, self.p_images['main_office'].width(), self.p_images['main_office'].height())
        self.main_office.setScaledContents(True)

        layout.addWidget(self.main_office)

        self.setLayout(layout)
        
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


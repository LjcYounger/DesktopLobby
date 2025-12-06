from PySide6.QtCore import QObject, Signal

class Communicator(QObject):
    # 创建一个信号类，用于传递数据
    data_signal = Signal(object)
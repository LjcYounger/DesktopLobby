from PySide6.QtCore import QObject, Signal


class SignalBus(QObject):
    settings_signal = Signal(str, object)  # key, value
    UI_windows_signal = Signal(str, object)  # key, value
    AI_settings_signal = Signal(str, str, object)  # ori_name, new_name, inf_dict
    dialog_anim_signal = Signal(str)  # ani_name

    AI_start_signal = Signal(str, object)  # name, inf_dict
    AI_generate_send_signal = Signal(object)  # dict
    AI_generate_get_signal = Signal(object)  # dict
    AI_dialog_input_signal = Signal(str)  # content

    debug_show_signal = Signal(bool)

    print_signal = Signal(str)
    close_signal = Signal()

    def __init__(self):
        super().__init__()


signal_bus = SignalBus()

from custom_QDialog import CustomQDialog as QDialog
from PySide6.QtWidgets import (QLabel,
                             QVBoxLayout,
                             QCheckBox,
                             QHBoxLayout,
                             QTableWidget,
                             QTableWidgetItem,
                             QAbstractItemView,
                             QFrame,
                             QSpinBox,
                             QPushButton)
from PySide6.QtGui import QColor
from communicator import Communicator

from getResources import GLOBAL_CONFIG
from database.database import db_load_character_intro, db_delete_conversation_record, db_get_AI_save_config
from signal_bus import signal_bus


class AISettingsWindow(QDialog):
    def __init__(self, CNAME: list):
        super().__init__()

        self.key_table_elements = []
        for save_name in GLOBAL_CONFIG.AI_SAVES:
            try:
                config, _ = db_get_AI_save_config(save_name)
            except Exception as e:
                print(f"[ERROR]AI Save Loading Error: {e}")
            else:
                from json import dumps
                self.key_table_elements.append({save_name: dumps(config)})
        self.setWindowTitle(GLOBAL_CONFIG.LANGUAGE.get("AI settings", ""))
        self.setFixedWidth(400)

        layout = QVBoxLayout()

        l1 = QHBoxLayout()

        l1.addStretch()

        start_button = QPushButton()
        start_button.setText(GLOBAL_CONFIG.LANGUAGE.get("Start AI", ""))
        l1.addWidget(start_button)

        key_add_button = QPushButton()
        key_add_button.setText(GLOBAL_CONFIG.LANGUAGE.get('Add', ""))
        l1.addWidget(key_add_button)

        key_edit_button = QPushButton()
        key_edit_button.setText(GLOBAL_CONFIG.LANGUAGE.get("Edit", ""))
        l1.addWidget(key_edit_button)

        key_delete_button = QPushButton()
        key_delete_button.setText(GLOBAL_CONFIG.LANGUAGE.get('Delete', ""))
        l1.addWidget(key_delete_button)

        layout.addLayout(l1)

        l2 = QHBoxLayout()
        self.key_table = QTableWidget(self)
        self.key_table.setRowCount(100)
        self.key_table.setColumnCount(2)
        self.key_table.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.key_table.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.key_table.setHorizontalHeaderLabels([GLOBAL_CONFIG.LANGUAGE.get("Name", ""), GLOBAL_CONFIG.LANGUAGE.get("Information", "")])
        for x in [(0, 60), (1, 340)]:
            self.key_table.setColumnWidth(*x)
        for x in range(0, 100):
            self.key_table.setRowHeight(x, 10)

        self._update_key_table()

        self.key_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.key_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.key_table.setSelectionMode(QTableWidget.SingleSelection)
        l2.addWidget(self.key_table)

        l21 = QVBoxLayout()

        l21.addSpacing(32)

        message1 = QLabel()
        message1.setText(GLOBAL_CONFIG.LANGUAGE.get("<-Using", ""))
        l21.addWidget(message1)

        l21.addStretch()

        key_change_button = QPushButton()
        key_change_button.setText(GLOBAL_CONFIG.LANGUAGE.get("Change", ""))
        l21.addWidget(key_change_button)

        l21.addStretch()

        l2.addLayout(l21)
        layout.addLayout(l2)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("color: gray;")
        line.setLineWidth(1)
        layout.addWidget(line)

        message2 = QLabel()
        message2.setText(GLOBAL_CONFIG.LANGUAGE.get("Current Character Settings", ""))
        layout.addWidget(message2)

        l3 = QHBoxLayout()

        #OTDcheck = QCheckBox(GLOBAL_CONFIG.LANGUAGE.get("Offer to Dialogue", ""), self)
        #OTDcheck.setChecked(False)
        #l3.addWidget(OTDcheck)

        SDRcheck = QCheckBox(GLOBAL_CONFIG.LANGUAGE.get("Save Dialog Record", ""), self)
        SDRcheck.setChecked(True)
        l3.addWidget(SDRcheck)

        layout.addLayout(l3)

        l5 = QHBoxLayout()

        message5 = QLabel()
        message5.setText(GLOBAL_CONFIG.LANGUAGE.get("Clean Dialog Record Before", ""))
        l5.addWidget(message5)

        CDRint = QSpinBox()
        CDRint.setMinimum(0)
        CDRint.setValue(30)
        l5.addWidget(CDRint)

        message6 = QLabel()
        message6.setText(GLOBAL_CONFIG.LANGUAGE.get("Days (0->clear)", ""))
        l5.addWidget(message6)

        CDR_button = QPushButton()
        CDR_button.setText(GLOBAL_CONFIG.LANGUAGE.get("Confirm", ""))
        l5.addWidget(CDR_button)

        layout.addLayout(l5)

        l6 = QHBoxLayout()

        RCI_button = QPushButton()
        RCI_button.setText(GLOBAL_CONFIG.LANGUAGE.get("Refresh Characters", ""))
        l6.addWidget(RCI_button)

        layout.addLayout(l6)

        self.setLayout(layout)

        start_button.pressed.connect(lambda: self.start_AI())
        key_add_button.clicked.connect(lambda: self.create_AI())
        key_edit_button.clicked.connect(lambda: self.modify_AI())
        key_delete_button.clicked.connect(lambda: self.delete_AI())
        key_change_button.clicked.connect(lambda: self.change_AI())

        SDRcheck.stateChanged.connect(lambda: signal_bus.settings_signal.emit("AI_save_state", SDRcheck.checkState()))
        CDR_button.pressed.connect(lambda: db_delete_conversation_record(CDRint.value(), character=CNAME))
        RCI_button.pressed.connect(lambda: db_load_character_intro(force_reload=True))

        signal_bus.AI_settings_signal.connect(self.modify_key_table)

    def modify_key_table(self, ori_name, new_name, inf_dict):
        if ori_name:
            if new_name and inf_dict:
                # 修改
                for i, row in enumerate(self.key_table_elements):
                    if ori_name in row.keys():
                        self.key_table_elements[i] = {new_name: inf_dict}
                        for j, cell in enumerate((new_name, inf_dict)):
                            self.key_table.setItem(i, j, QTableWidgetItem(str(cell)))
            else:
                # 删除
                key_table_elements_keys = tuple(element.keys() for element in self.key_table_elements)
                for i, element in enumerate(key_table_elements_keys):
                    if ori_name in element:
                        del self.key_table_elements[i]
                self._update_key_table()

        else:
            # 新建
            self.key_table_elements.append({new_name: inf_dict})
            for j, cell in enumerate((new_name, inf_dict)):
                self.key_table.setItem(len(self.key_table_elements) - 1, j, QTableWidgetItem(str(cell)))

        self.key_table.horizontalScrollBar().setValue(0)

    def _update_key_table(self):
        # 填充元素
        self.key_table.clearContents()
        for i, row in enumerate(self.key_table_elements):
            row = next(iter(row.items()))
            for j, cell in enumerate(row):
                self.key_table.setItem(i, j, QTableWidgetItem(str(cell)))

        # 设置第一行颜色为灰色
        gray_color = QColor(211, 211, 211)
        for col in range(self.key_table.columnCount()):
            item = self.key_table.item(0, col)
            if not item:
                item = QTableWidgetItem()
                self.key_table.setItem(0, col, item)
            item.setBackground(gray_color)

        # 水平进度条左移
        self.key_table.horizontalScrollBar().setValue(0)

        self.default_start_AI()
    def default_start_AI(self):
        if GLOBAL_CONFIG.PREFERENCES["defaultInitAI"] and GLOBAL_CONFIG.PREFERENCES["defaultAI"] in GLOBAL_CONFIG.AI_SAVES:
            from json import loads
            for element in self.key_table_elements:
                key, value = list(element.items())[0]
                if key == GLOBAL_CONFIG.PREFERENCES["defaultAI"]:
                    signal_bus.AI_start_signal.emit(key, loads(value) if type(value) == str else value)

    def start_AI(self):
        if self.key_table_elements:
            from json import loads
            line0 = list(self.key_table_elements[0].items())[0]
            signal_bus.AI_start_signal.emit(line0[0], loads(line0[1]) if type(line0[1]) == str else line0[1])

    def create_AI(self):
        from windows.AI_settings_operate_window import OperateAIWindow
        create_AI_window = OperateAIWindow('create')
        create_AI_window.show()

    def modify_AI(self):
        if (self.key_table.currentRow() != -1 and
                self.key_table_elements and
                self.key_table.currentRow() < len(self.key_table_elements)):
            from windows.AI_settings_operate_window import OperateAIWindow
            modified_AI_name = next(iter(self.key_table_elements[self.key_table.currentRow()].keys()))
            modify_AI_window = OperateAIWindow('modify', modified_AI_name=modified_AI_name)
            modify_AI_window.show()

    def delete_AI(self):
        if (self.key_table.currentRow() != -1 and
                self.key_table_elements and
                self.key_table.currentRow() < len(self.key_table_elements)):
            from windows.AI_settings_operate_window import DeleteAIWindow
            deleted_AI_name = next(iter(self.key_table_elements[self.key_table.currentRow()].keys()))
            delete_AI_window = DeleteAIWindow(deleted_AI_name)
            delete_AI_window.show()

    def change_AI(self):
        if (self.key_table.currentRow() != -1 and
                self.key_table_elements and
                self.key_table.currentRow() < len(self.key_table_elements)):
            self.key_table_elements.insert(0, self.key_table_elements.pop(self.key_table.currentRow()))

            self._update_key_table()

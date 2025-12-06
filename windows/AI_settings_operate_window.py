from PySide6.QtCore import Qt
from custom_QDialog import CustomQDialog as QDialog
from PySide6.QtWidgets import (QLabel,
                             QHBoxLayout,
                             QVBoxLayout,
                             QLineEdit,
                             QPushButton,
                             QCheckBox)
from typing import Literal

from getResources import GLOBAL_CONFIG
from functions.counter import counter
from database.database import db_get_AI_templates_config, db_create_AI_save, db_modify_AI_save, db_get_AI_save_config
from signal_bus import signal_bus

class OperateAIWindow(QDialog):
    counter = counter(len(GLOBAL_CONFIG.AI_TEMPLATES))

    def __init__(self, mode: Literal['create', 'modify'], modified_AI_name=''):
        super().__init__()
        self.mode = mode
        self.modified_AI_name = modified_AI_name

        if self.modified_AI_name:
            self.introduction = ""
            self.parameters, self.config = db_get_AI_save_config(self.modified_AI_name)

        else:
            self.config = db_get_AI_templates_config(GLOBAL_CONFIG.AI_TEMPLATES[OperateAIWindow.counter('get')])
            self.introduction = self.config.get('introduction', "")
            self.parameters = self.config['parameters']
        if self.mode == 'create':
            self.parameters['NAME'] = self.modified_AI_name

        self.setWindowTitle(self.mode + ' AI')
        self.setMinimumWidth(300)

        self.layout = QVBoxLayout()

        self.current_AI_label = QLabel()
        self.current_AI_label.setText(modified_AI_name if modified_AI_name else GLOBAL_CONFIG.AI_TEMPLATES[OperateAIWindow.counter('get')])
        self.current_AI_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.current_AI_label)

        self.introduction_label = QLabel()
        self.introduction_label.setText(self.introduction)
        self.introduction_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.introduction_label)

        self.boxes_layout = QVBoxLayout()
        self.boxes_init()

        button_layout = QHBoxLayout()

        if self.mode == 'create':
            last_button = QPushButton()
            last_button.setText(GLOBAL_CONFIG.LANGUAGE.get("Last One", ''))
            last_button.clicked.connect(lambda: self.switch('last'))
            button_layout.addWidget(last_button)

        confirm_button = QPushButton()
        confirm_button.setText(GLOBAL_CONFIG.LANGUAGE.get("Confirm", ''))
        confirm_button.setFixedWidth(120)
        confirm_button.clicked.connect(lambda: self.confirm())
        button_layout.addWidget(confirm_button)

        if self.mode == 'create':
            next_button = QPushButton()
            next_button.setText(GLOBAL_CONFIG.LANGUAGE.get("Next One", ''))
            next_button.clicked.connect(lambda: self.switch('next'))
            button_layout.addWidget(next_button)

        self.layout.addLayout(button_layout)

        self.setLayout(self.layout)

    def boxes_init(self):
        # {key: [QLabel, QLineEdit]}
        self.boxes = {}

        for key, value in self.parameters.items():
            para_layout = QHBoxLayout()
            self.boxes[key] = []

            text_box = QLabel()
            text_box.setAlignment(Qt.AlignmentFlag.AlignCenter)  # 文本靠右
            text_box.setText(key)
            para_layout.addWidget(text_box)
            self.boxes[key].append(text_box)

            edit_box = QLineEdit()
            edit_box.setFixedWidth(220)
            if type(value) == str:
                edit_box.setText(value)
            para_layout.addWidget(edit_box)
            self.boxes[key].append(edit_box)

            self.boxes_layout.addLayout(para_layout)
        self.layout.addLayout(self.boxes_layout)

    def switch(self, type: Literal['last', 'next']):
        OperateAIWindow.counter(type)
        self.config = db_get_AI_templates_config(GLOBAL_CONFIG.AI_TEMPLATES[OperateAIWindow.counter('get')])
        self.introduction = self.config.get('introduction', "")
        self.parameters = self.config['parameters']
        self.parameters['NAME'] = ""

        # 修改text
        self.current_AI_label.setText(GLOBAL_CONFIG.AI_TEMPLATES[OperateAIWindow.counter('get')])
        self.introduction_label.setText(self.introduction)

        # 删除之前的self.boxes()
        for text_box, edit_box in self.boxes.values():
            text_box.deleteLater()
            edit_box.deleteLater()

        self.boxes_init()

    def confirm(self):
        para_dict = {text_box.text(): edit_box.text() for text_box, edit_box in self.boxes.values()}
        try:
            if self.mode == 'create':
                # 复制文件
                import shutil
                shutil.copytree(f"AI/TEMPLATES/{GLOBAL_CONFIG.AI_TEMPLATES[OperateAIWindow.counter('get')]}",
                                f"AI/{para_dict['NAME']}")

                db_create_AI_save(para_dict['NAME'], para_dict, self.config)
                signal_bus.AI_settings_signal.emit('', para_dict['NAME'], para_dict)
            elif self.mode == 'modify' and self.modified_AI_name:
                db_modify_AI_save(self.modified_AI_name, para_dict['NAME'], para_dict, self.config)
                if self.modified_AI_name != para_dict['NAME']:
                    # 重命名文件
                    import os
                    os.rename(f"AI/{self.modified_AI_name}", f"AI/{para_dict['NAME']}")
                signal_bus.AI_settings_signal.emit(self.modified_AI_name, para_dict['NAME'], para_dict)

        except FileExistsError:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(None, "错误", "重复名称")
        else:
            self.close()


class DeleteAIWindow(QDialog):
    def __init__(self, ai_name):
        super().__init__()
        self.ai_name = ai_name

        layout = QVBoxLayout()

        text_label = QLabel()
        text_label.setText("你确定要删除吗?")
        layout.addWidget(text_label)

        self.delete_file_check = QCheckBox("同时删除文件", self)
        self.delete_file_check.setChecked(False)
        layout.addWidget(self.delete_file_check)

        button_layout = QHBoxLayout()

        button_layout.addStretch()

        cancel_button = QPushButton()
        cancel_button.setText("取消")
        cancel_button.setFixedWidth(120)
        button_layout.addWidget(cancel_button)

        confirm_button = QPushButton()
        confirm_button.setText("确认")
        confirm_button.setFixedWidth(120)
        button_layout.addWidget(confirm_button)

        button_layout.addStretch()

        layout.addLayout(button_layout)

        self.setLayout(layout)

        cancel_button.clicked.connect(lambda: self.close())
        confirm_button.clicked.connect(self.delete_AI)

    def delete_AI(self):
        from database.database import db_delete_AI_save
        db_delete_AI_save(self.ai_name)
        signal_bus.AI_settings_signal.emit(self.ai_name, "", {})

        if self.delete_file_check.checkState():
            import shutil
            import os
            if os.path.exists(f"AI/{self.ai_name}"):
                shutil.rmtree(f"AI/{self.ai_name}")

        self.close()
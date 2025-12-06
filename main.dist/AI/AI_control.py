import importlib.util
from database.database import *
from signal_bus import signal_bus
from PySide6.QtCore import QObject
import time


class AI(QObject):
    def __init__(self, AI_name, inf_dict):
        super().__init__()
        spec = importlib.util.spec_from_file_location("getCharacter", f"AI/{AI_name}/AI.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.AI_class = module.AI(inf_dict)
        self.current_character = ''
        self.records = []
        self.character_inf = {}
        self.b = False
        self.save = True

        signal_bus.AI_generate_send_signal.connect(self.generate_result)
    def generate_result(self, data: dict, debug=False):
        """
        data.keys: current_character, user_content, example(alternative)
        """
        self.user_content = data['user_content']
        example = data.get('example', '')

        # 更换角色
        if self.current_character != data['current_character'] or not self.character_inf:
            self.current_character = data['current_character']
            self.character_inf = db_get_character_intro(name=self.current_character)
            self.records = db_get_conversation_record(self.current_character)
        if self.b:
            self.records = []
        if self.save:
            self.records.append({'role': 'user', 'content': self.user_content})
            db_add_conversation_record(name=self.current_character,
                                       role='user',
                                       content=self.user_content,
                                       emotion='0',
                                       beginning=self.b,
                                       dateF=time.time(),
                                       total_tokens=0)
        self.b = False
        prompt = self.AI_class.generate_AI_prompt(self.current_character, **self.character_inf, example=example)
        try:
            content_list, emotion, total_tokens = self.AI_class.get_answer_from_AI(self.records, prompt)
        except Exception as e:
            print(f"[ERROR]AI Error: {e}")
            content_list, emotion, total_tokens = ["出错了呢", str(e)], 'default', -1
        else:
            if self.save:
                self.records.append({'role': 'assistant', 'content': ''.join(content_list) + f'#{emotion}#'})
                db_add_conversation_record(name=self.current_character,
                                           role='assistant',
                                           content=''.join(content_list),
                                           emotion=emotion,
                                           beginning=False,
                                           dateF=time.time(),
                                           total_tokens=total_tokens)
        print(f"[DEBUG]Dialog Records: {self.records}")

        if debug:
            return f"{content_list}#{emotion}#"
        else:
            signal_bus.AI_generate_get_signal.emit({'content_list': content_list, 'emotion': emotion})

import importlib.util
from database.database import *
from signal_bus import signal_bus
from PySide6.QtCore import QObject, QThread, Signal
import time


class AI(QObject):
    # 添加初始化完成信号
    initialization_finished = Signal()
    
    def __init__(self, AI_name, inf_dict):
        super().__init__()
        self.AI_name = AI_name
        self.inf_dict = inf_dict
        self.current_character = ''
        self.records = []
        self.character_inf = {}
        self.b = False
        self.save = True
        self.AI_class = None
        self.is_initialized = False
        
        # 创建初始化线程
        self.init_thread = AIInitThread(AI_name, inf_dict)
        self.init_thread.initialization_complete.connect(self.on_initialization_complete)
        self.init_thread.error_occurred.connect(self.on_initialization_error)
        
        # 创建推理线程池
        self.inference_thread = None
        
        signal_bus.AI_generate_send_signal.connect(self.generate_result)
    
    def start_initialization(self):
        """开始异步初始化"""
        print("[INFO]Starting AI initialization in background thread...")
        self.init_thread.start()
    
    def on_initialization_complete(self, AI_instance):
        """初始化完成回调"""
        self.AI_class = AI_instance
        self.is_initialized = True
        print("[INFO]AI initialization completed!")
        self.initialization_finished.emit()
    
    def on_initialization_error(self, error_msg):
        """初始化错误回调"""
        print(f"[ERROR]AI initialization failed: {error_msg}")
        self.is_initialized = False
        # 可以在这里发送错误信号给UI
    
    def generate_result(self, data: dict, debug=False):
        """
        data.keys: current_character, user_content, example(alternative)
        """
        # 检查是否已初始化
        if not self.is_initialized:
            print("[WARNING]AI not initialized yet, please wait...")
            return
            
        if self.AI_class is None:
            print("[ERROR]AI instance is None")
            return
            
        # 创建推理线程来处理耗时操作
        if self.inference_thread and self.inference_thread.isRunning():
            print("[WARNING]Previous inference still running, waiting...")
            self.inference_thread.wait()
            
        self.inference_thread = AIInferenceThread(
            self.AI_class, 
            data, 
            self.current_character,
            self.character_inf,
            self.records,
            self.b,
            self.save
        )
        self.inference_thread.inference_complete.connect(self.on_inference_complete)
        self.inference_thread.inference_error.connect(self.on_inference_error)
        self.inference_thread.start()
    
    def on_inference_complete(self, result_data):
        """推理完成回调"""
        content_list, emotion, updated_records = result_data['result']
        self.records = updated_records
        self.b = False
        
        if not result_data['debug']:
            signal_bus.AI_generate_get_signal.emit({
                'content_list': content_list, 
                'emotion': emotion
            })
        else:
            return f"{content_list}#{emotion}#"
    
    def on_inference_error(self, error_msg):
        """推理错误回调"""
        print(f"[ERROR]AI inference failed: {error_msg}")
        # 发送错误信号给UI
        signal_bus.AI_generate_get_signal.emit({
            'content_list': ["出错了呢"], 
            'emotion': 'default'
        })


class AIInitThread(QThread):
    """专门用于AI初始化的线程"""
    initialization_complete = Signal(object)  # 传递初始化好的AI实例
    error_occurred = Signal(str)  # 传递错误信息
    
    def __init__(self, AI_name, inf_dict):
        super().__init__()
        self.AI_name = AI_name
        self.inf_dict = inf_dict
    
    def run(self):
        try:
            print(f"[DEBUG]Loading AI module: AI/{self.AI_name}/AI.py")
            spec = importlib.util.spec_from_file_location("getCharacter", f"AI/{self.AI_name}/AI.py")
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            print("[DEBUG]Creating AI instance...")
            AI_instance = module.AI(self.inf_dict)
            
            print("[DEBUG]AI initialization successful")
            self.initialization_complete.emit(AI_instance)
            
        except Exception as e:
            error_msg = f"Failed to initialize AI: {str(e)}"
            print(f"[ERROR]{error_msg}")
            self.error_occurred.emit(error_msg)


class AIInferenceThread(QThread):
    """专门用于AI推理的线程"""
    inference_complete = Signal(dict)  # 传递推理结果
    inference_error = Signal(str)     # 传递错误信息
    
    def __init__(self, AI_class, data, current_character, character_inf, records, b, save):
        super().__init__()
        self.AI_class = AI_class
        self.data = data
        self.current_character = current_character
        self.character_inf = character_inf
        self.records = records.copy()  # 复制记录避免线程安全问题
        self.b = b
        self.save = save
    
    def run(self):
        try:
            user_content = self.data['user_content']
            example = self.data.get('example', '')
            new_character = self.data['current_character']
            
            # 更新角色信息（如果需要）
            if self.current_character != new_character or not self.character_inf:
                self.current_character = new_character
                self.character_inf = db_get_character_intro(name=self.current_character)
                self.records = db_get_conversation_record(self.current_character)
            
            if self.b:
                self.records = []
                
            if self.save:
                self.records.append({'role': 'user', 'content': user_content})
                db_add_conversation_record(
                    name=self.current_character,
                    role='user',
                    content=user_content,
                    emotion='0',
                    beginning=self.b,
                    dateF=time.time(),
                    total_tokens=0
                )
            
            prompt = self.AI_class.generate_AI_prompt(
                self.current_character, 
                **self.character_inf, 
                example=example
            )
            
            # 在子线程中执行推理
            content_list, emotion, total_tokens = self.AI_class.get_answer_from_AI(
                self.records, 
                prompt
            )
            
            if self.save:
                self.records.append({
                    'role': 'assistant', 
                    'content': ''.join(content_list) + f'#{emotion}#'
                })
                db_add_conversation_record(
                    name=self.current_character,
                    role='assistant',
                    content=''.join(content_list),
                    emotion=emotion,
                    beginning=False,
                    dateF=time.time(),
                    total_tokens=total_tokens
                )
            
            result_data = {
                'result': (content_list, emotion, self.records),
                'debug': self.data.get('debug', False)
            }
            
            self.inference_complete.emit(result_data)
            
        except Exception as e:
            error_msg = f"AI inference error: {str(e)}"
            print(f"[ERROR]{error_msg}")
            self.inference_error.emit(error_msg)
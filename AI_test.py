#from database.database import *
from AI.AI_control import AI

a=AI('4', {'NAME': "4", "PATH": "D:/gguf_models/qwen1_5-4b-chat-q4_k_m.gguf"})
#db_delete_conversation_record(0, character='mi')
while True:
    x=input()
    if x == 's':
        break
    elif x == 'b':
        a.b = True
    else:
        print('结果', a.generate_result({'user_content': x, 'current_character': 'momoi', 'example': "老师，我要玩游戏！！！！！#smile#"}, debug=True))

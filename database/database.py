from peewee import (SqliteDatabase, Model,
                    CharField, IntegerField, BooleanField, FloatField)
from getResources import GLOBAL_CONFIG
from functions.json_ import load_json
from resource_loader import getCharacterIntroduction
from loadingWindow.loading import LoadingWindowControl
import time

db = SqliteDatabase('database/database.db')
db.connect()


class Character(Model):
    code_name = CharField()
    name = CharField()
    introduction = CharField()
    emotion = CharField()
    birthday = IntegerField()
    hobby = CharField()

    class Meta:
        database = db


class Conversation(Model):
    name = CharField()
    role = CharField()
    content = CharField()
    emotion = CharField()
    beginning = BooleanField()
    date = CharField()
    dateF = FloatField()
    total_tokens = IntegerField()

    class Meta:
        database = db


class AI_Saves(Model):
    name = CharField()
    inf_dict = CharField()
    config_dict = CharField()
    dateF = FloatField()

    class Meta:
        database = db


class AI_Templates(Model):
    name = CharField()
    config_dict = CharField()

    class Meta:
        database = db


# print(Character.select().where(Character.name=='Mika').get())
def db_reload_character_intro(code_name):
    introduction, hobby, emotion = getCharacterIntroduction(code_name)
    name = GLOBAL_CONFIG.CONTRAST.get(code_name, code_name)
    Character.create(code_name=code_name, name=name, introduction=introduction, emotion=emotion, hobby=hobby,
                     birthday='01-01')


def db_load_character_intro(force_reload=False):
    if force_reload:
        Character.delete().execute()
    db_character_code_names = [x.code_name for x in Character.select()]
    for code_name in GLOBAL_CONFIG.CODE_NAMES:
        if code_name not in db_character_code_names:
            LoadingWindowControl.messageLoadingWindow(f"[database] character:{code_name}")
            db_reload_character_intro(code_name)


def db_get_character_intro(code_name=None, name=None):
    """
    return: introduction, hobby, emotions
    """
    if code_name:
        cha = Character.select().where(Character.code_name == code_name).first()

    elif name:
        cha = Character.select().where(Character.name == name).first()
    return {"introduction": cha.introduction, "hobby": cha.hobby, "emotions": cha.emotion}


def db_reload_AI_template(ai_name):
    config = load_json(f"AI/TEMPLATES/{ai_name}/config.json", to_string=True)
    AI_Templates.create(name=ai_name, config_dict=config)


def db_load_AI_templates(force_reload=False):
    if force_reload:
        AI_Templates.delete().execute()
    db_ai_names = [x.name for x in AI_Templates.select()]
    for ai_name in GLOBAL_CONFIG.AI_TEMPLATES:
        if ai_name not in db_ai_names:
            LoadingWindowControl.messageLoadingWindow(f"[database] AI:{ai_name}")
            db_reload_AI_template(ai_name)


def db_get_AI_templates_config(name: str) -> dict:
    from json import loads
    line_config = AI_Templates.select().where(AI_Templates.name == name).first()
    return loads(line_config.config_dict)


def db_create_AI_save(name: str, parameters, config_dict):
    from json import dumps
    from functions.cipher import encrypt_api_key

    # 加密
    parameters_copy = parameters.copy()
    for key, value in parameters.items():
        if type(config_dict['parameters'][key]) == dict:
            if config_dict['parameters'][key]['secret']:
                parameters_copy[key] = encrypt_api_key(value, parameters['NAME'])

    AI_Saves.create(name=name, inf_dict=dumps(parameters_copy), config_dict=dumps(config_dict), dateF=time.time())


def db_modify_AI_save(ori_name: str, new_name: str, parameters, config_dict):
    db_delete_AI_save(ori_name)
    db_create_AI_save(new_name, parameters, config_dict)

def db_delete_AI_save(name: str):
    AI_Saves.delete().where(AI_Saves.name == name).execute()

def db_get_AI_save_config(name: str) -> (dict, dict):
    from json import loads
    from functions.cipher import decrypt_api_key

    line_config = AI_Saves.select().where(AI_Saves.name == name).first()
    parameters = loads(line_config.inf_dict)
    config_dict = loads(line_config.config_dict)

    # 解密
    parameters_copy = parameters.copy()
    for key, value in parameters.items():
        if type(config_dict['parameters'][key]) == dict:
            if config_dict['parameters'][key]['secret']:
                parameters_copy[key] = decrypt_api_key(value, parameters['NAME'])

    return parameters_copy, config_dict


def db_add_conversation_record(**kwargs):
    """
    name, role, content, emotion, beginning, dateF, total_tokens
    """
    date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(kwargs['dateF']))
    Conversation.create(**kwargs, date=date)


def db_get_conversation_record(character):
    records = []
    query = Conversation.select().where(Conversation.name == character).order_by(Conversation.dateF.desc())
    for record in query:
        if record.beginning:
            break
        content = f"{record.content}#{record.emotion}#" if record.emotion != '0' else record.content
        records.append({'role': record.role, 'content': content})

    records.reverse()
    return records


def db_delete_conversation_record(day, character='all'):
    Ddate = time.time() - day * 24 * 60 * 60
    if character == 'all':
        Conversation.delete().where(Conversation.dateF < Ddate).execute()
    else:
        Conversation.delete().where(Conversation.name == character, Conversation.dateF < Ddate).execute()


if not db.get_tables():
    # 创建表
    db.create_tables([Character, Conversation, AI_Saves, AI_Templates])
    db_load_character_intro()
    db_load_AI_templates()

if __name__ == "__main__":
    db_load_character_intro()
    db_load_AI_templates(True)
    db_load_AI_saves(True)
    db_delete_conversation_record(0)
    # for a in range(100):
    #    db_add_conversation_record(name='mika', role='assistant', content=f"就开始多少{a}", emotion='Happy', beginning=False, dateF=time.time(), total_tokens=123)
    r = db_get_conversation_record('mika')
    print(r)

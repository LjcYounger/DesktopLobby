import importlib.util
from functions.json_ import load_json
import os


def getCharacterInf(name):
    spec = importlib.util.spec_from_file_location("getCharacter", f"characters/{name}/getCharacter.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.getCharacter(name)


def getCharacterIntroduction(name):
    content = load_json(f"characters/{name}/introduction.json", to_json=False).replace('\n', '')
    intro, hoem = content.split("[hobby]")
    hobby, emotion = hoem.split("[emotion]")
    return intro, hobby, emotion


def get_folder_resources(path: str, required: list, excluded: list = []):
    required = set(required)
    floder_names = []
    for ch in os.listdir(path):
        if os.path.isdir(os.path.join(path, ch)) and not ch in excluded:
            # 确认所需文件在文件夹里均存在
            found = set(os.listdir(os.path.join(path, ch)))
            if required <= found:  # 子集
                floder_names.append(ch)
    return floder_names


if __name__ == '__main__':
    print(get_folder_resources('characters', ['dialogBoxContent.json', 'introduction.json', 'getCharacter.py']))
    print(get_folder_resources('AI/TEMPLATES', ['AI.py', 'config.json']))
    print(get_folder_resources('AI', ['AI.py']))

from PIL import Image
import os
from functions.json_ import load_json
from loadingWindow.loading import LoadingWindowControl
from dataclasses_ import GlobalConfig, GlobalVariables
from resource_loader import get_folder_resources
from job_object import create_job_object

def loadFont(path, size, type=None, italic=False):
    from PySide6.QtGui import QFont, QFontDatabase
    if not type:
        type = QFont.Normal
    fontid = QFontDatabase.addApplicationFont(path)
    if fontid == -1:
        return None
    families = QFontDatabase.applicationFontFamilies(fontid)
    if not families:
        return None
    font = QFont()
    font.setFamily(families[0])
    font.setPointSize(size)
    font.setWeight(type)
    font.setItalic(italic)
    return font


CODE_NAMES = get_folder_resources('characters', ['dialogBoxContent.json', 'introduction.json', 'getCharacter.py'])
print(f"[DEBUG]Characters: {CODE_NAMES}")
AI_NAMES = get_folder_resources('AI', ['AI.py', 'config.json'])
print(f"[DEBUG]AI Saves: {AI_NAMES}")
AI_TEMPLATES = get_folder_resources('AI/TEMPLATES', ['AI.py', 'config.json'])
print(f"[DEBUG]AI Templates: {AI_TEMPLATES}")
PREFERENCES = load_json("preferences.json")
CONTRAST = load_json("contrast.json")
DIALOGBOX_INF = load_json("images/Lobby_balloon.json")
LANGUAGE = load_json(f"lang/{PREFERENCES['language']}.lang")

JOB_OBJECT = create_job_object()

GLOBAL_CONFIG = GlobalConfig(CODE_NAMES, AI_NAMES, AI_TEMPLATES, PREFERENCES, CONTRAST, DIALOGBOX_INF, LANGUAGE, JOB_OBJECT,
                             ZOOM_SCALE=PREFERENCES["zoomScale"])
global_variables = GlobalVariables()

LoadingWindowControl.messageLoadingWindow("Global configuration loading completed.")

tempfolderPath = os.path.join(os.getenv('TEMP'), 'DesktopLobby')
os.makedirs(tempfolderPath, exist_ok=True)
tempCharacterPath = os.path.join(tempfolderPath, "currentCharacter.json")
LoadingWindowControl.messageLoadingWindow("File creation completed.")


def setCurrentCharacter(characterName):
    with open(tempCharacterPath, 'w') as txt:
        txt.write(characterName)


def getCurrentCharacter():
    if not os.path.exists(tempCharacterPath):
        setCurrentCharacter(PREFERENCES['initialCharacter'])
    with open(tempCharacterPath, 'r') as txt:
        characterName = txt.read()
    return characterName


def getImageGroup(name):
    with open(f"images/{name}.asset", 'r') as txt:
        content = txt.readlines()
    mPixelSize = float(content[-2][(content[-2].find(':') + 2): -1])

    orimage = Image.open(f"images/{name}.png").convert("RGBA")
    images = {}
    for a in range(16, len(content) - 13, 13):
        x = int(content[a + 1][(content[a + 1].find(':') + 2): -1])
        y = int(content[a + 2][(content[a + 2].find(':') + 2): -1])
        w = int(content[a + 3][(content[a + 3].find(':') + 2): -1])
        h = int(content[a + 4][(content[a + 4].find(':') + 2): -1])
        region = orimage.crop((x, y, x + w, y + h))
        if mPixelSize != 1.0:
            region = region.resize((w * a, h * a))
        name = content[a][(content[a].find(':') + 2): -1]
        images[name] = region
    return images


def getImage(gname, iname):
    with open(f"images/{gname}.asset", 'r') as txt:
        content = txt.readlines()
    orimage = Image.open(f"images/{gname}.png").convert("RGBA")
    for a in range(16, len(content) - 13, 13):
        if content[a][(content[a].find(':') + 2): -1] == iname:
            x = int(content[a + 1][(content[a + 1].find(':') + 2):])
            y = int(content[a + 2][(content[a + 2].find(':') + 2):])
            w = int(content[a + 3][(content[a + 3].find(':') + 2):])
            h = int(content[a + 4][(content[a + 4].find(':') + 2):])
            image = orimage.crop((x, y, x + w, y + h))
            break
    return image


def getDialogBoxContent(name):
    return load_json(f"characters/{name}/dialogBoxContent.json")

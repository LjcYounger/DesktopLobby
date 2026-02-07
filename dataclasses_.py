from dataclasses import dataclass
from typing import Any, Dict, List

@dataclass
class GlobalConfig:
    CODE_NAMES: List[str] = None
    AI_SAVES: List[str] = None
    AI_TEMPLATES: List[str] = None
    PREFERENCES: Dict = None
    CONTRAST: Dict = None
    DIALOGBOX_INF: Dict = None
    LANGUAGE: Dict = None

    JOB_OBJECT: Any = None

    ANIMS: List[Any] = None

    k00: float = 1
    ZOOM_SCALE: float = 1.1962



@dataclass
class GlobalVariables:
    socket_thread: Any = None

    current_AI: Any = None

@dataclass
class CharacterConfig:
    name: str
    k0: float
    pictures: Dict
    settings: Dict
    emotions: Any
    halo_height: int
    dialogBoxImages: Any
    dialogBoxContent: Dict
    firstTime: bool
    today_is_birthday_sensei: bool
    screen: Any

@dataclass
class SettingsParameters:
    emotion: str = ''
    blink: bool = True #blinkable
    dialog: bool = True
    move: bool = False#movable
    size: float = 1.0
    close: bool = True#closable
    top_level: bool = False
    voice_volume: float = 1.0
    character: str = ''

    AI_open_new_topic: int = 0


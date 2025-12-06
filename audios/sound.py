from pygame import mixer, sndarray
from functools import lru_cache

mixer.init()

def _create_silent_sound(duration_ms=1000):
    """
    纯代码创建一个无声音频的 Sound 对象。

    Args:
        duration_ms (int): 静音的时长，单位为毫秒。默认为 1000ms (1秒)。

    Returns:
        pygame.mixer.Sound: 一个代表静音的 Sound 对象。
    """
    import numpy as np
    # 1. 获取当前混音器的设置
    # 这些设置必须与 pygame.mixer.init() 时的设置一致。
    # 如果你没有显式初始化，pygame会使用默认设置。
    freq, size, channels = mixer.get_init()
    # `size` 是位深度，如 -16 表示 16 位有符号整数。

    # 2. 计算需要多少个样本点
    # 采样率 (freq) 表示每秒的样本数。
    # duration_ms / 1000.0 将毫秒转换为秒。
    num_samples = int((duration_ms / 1000.0) * freq)

    # 3. 根据声道数创建静音数组
    if channels == 1:
        # 单声道: 创建一个一维数组
        silent_array = np.zeros(num_samples, dtype=np.int16)
    else:
        # 立体声: 创建一个二维数组，形状为 (num_samples, channels)
        silent_array = np.zeros((num_samples, channels), dtype=np.int16)
        # 注意：对于立体声，我们也可以用 `np.zeros((num_samples, 2))`

    # 4. 将 NumPy 数组转换为 Pygame Sound 对象
    silent_sound = sndarray.make_sound(silent_array)

    return silent_sound

def play_background_music(path):
    mixer.music.stop()
    mixer.music.load(path)
    mixer.music.play(-1)

@lru_cache(maxsize=128)
def load_audio_file(path):
    try:
        print(f"[DEBUG]Sound '{path}' loaded")
        sound = mixer.Sound(path)
    except Exception as e:
        print(f"[ERROR]Sound '{path}' Loading Failed: {e}")
        sound = _create_silent_sound()
    return sound

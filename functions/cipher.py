import keyring
import secrets
from cryptography.fernet import Fernet
from base64 import urlsafe_b64encode

SERVICE_NAME = "DesktopLobby"

def get_or_create_master_key(MASTER_KEY_ID):
    # 尝试从系统钥匙串获取主密钥
    master_key = keyring.get_password(SERVICE_NAME, MASTER_KEY_ID)
    if master_key is None:
        # 第一次运行：生成主密钥并保存
        raw_key = secrets.token_bytes(32)  # 256位
        master_key = urlsafe_b64encode(raw_key).decode()
        keyring.set_password(SERVICE_NAME, MASTER_KEY_ID, master_key)
    return master_key


def encrypt_api_key(api_key: str, MASTER_KEY_ID) -> str:
    master_key = get_or_create_master_key(MASTER_KEY_ID)
    f = Fernet(master_key.encode())
    token = f.encrypt(api_key.encode())
    return str(token, encoding='utf-8')


def decrypt_api_key(token: str, MASTER_KEY_ID) -> str:
    try:
        master_key = keyring.get_password(SERVICE_NAME, MASTER_KEY_ID)
        if not master_key:
            raise RuntimeError("主密钥未找到，请先设置 API Key")

        f = Fernet(master_key.encode())
        return f.decrypt(bytes(token, encoding='utf-8')).decode()
    except Exception as e:
        raise RuntimeError(f"解密失败：可能是文件损坏或系统账户变更") from e

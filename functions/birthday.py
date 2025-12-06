def _judgeBirthdayPlayer(birthdayDate, date_format="%m-%d"):
    import time
    try:
    # 获取当前时间的月日部分
        current_month_day = time.strftime(date_format)
    
    # 将给定日期字符串解析为时间元组
        given_time_tuple = time.strptime(birthdayDate, date_format)
        given_month_day = time.strftime(date_format, given_time_tuple)
    
    # 比较两个日期字符串
        if given_month_day == current_month_day:return True
        else:return False
    except ValueError as e:
        print(f"[ERROR]Date Format Error: {e}")
        return False

import os
from getResources import tempfolderPath
tempBirthdayPath=os.path.join(tempfolderPath, "senseiBirthday.data")

def setBirthdayDate(date: str):
    """在临时文件目录储存sensei生日"""
    from functions.cipher import encrypt_api_key
    result=encrypt_api_key(date, 'birthday')

    with open(tempBirthdayPath, 'w') as txt:
        txt.write(str(result))
def getBirthdayDate():
    """从临时文件目录获取sensei生日"""
    try:
        from functions.cipher import decrypt_api_key
        with open(tempBirthdayPath, 'r') as txt:
            data=txt.read()
        senseiBirthday = decrypt_api_key(data, 'birthday')
    except (FileNotFoundError, PermissionError, RuntimeError) as e:
        senseiBirthday = None
    return senseiBirthday
 
def getIftodayIsSenseiBirthday(app, screen, force_show=False):
    birthday_sensei=getBirthdayDate()
    if not birthday_sensei or force_show:
        from windows.UI_enter_birthday_date_window import UI_EnterBirthdayDateWindow
        EBDWindow=UI_EnterBirthdayDateWindow((screen.size().width(), screen.size().height()))
        app.exec()
        birthday_sensei=getBirthdayDate()
    if birthday_sensei:
        return _judgeBirthdayPlayer(birthday_sensei)
    else:
        return False
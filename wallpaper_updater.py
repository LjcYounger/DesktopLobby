import win32con
import win32gui
import win32api
import win32com.client
import os
import time
import sys
import winreg
from os.path import abspath, exists, join, dirname
from datetime import datetime

def get_current_wallpaper_from_registry():
    """从注册表读取当前壁纸路径"""
    try:
        # 壁纸路径存储在注册表 HKEY_CURRENT_USER\Control Panel\Desktop 的 Wallpaper 键值中
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Control Panel\Desktop", 0, winreg.KEY_READ)
        wallpaper_path, _ = winreg.QueryValueEx(key, "Wallpaper")
        winreg.CloseKey(key)
        return wallpaper_path
    except Exception as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 读取注册表壁纸路径失败: {e}")
        return None

def get_target_wallpaper_path():
    """从w.txt文件中读取目标壁纸路径"""
    txt_path = "w.txt"
    
    if exists(txt_path):
        with open(txt_path, 'r', encoding='utf-8') as f:
            path = f.read().strip()
            return path
    return None

def set_wallpaper(path):
    """设置壁纸并更新注册表"""
    abs_path = abspath(path)
    if exists(abs_path):
        try:
            # 设置壁纸
            win32gui.SystemParametersInfo(
                win32con.SPI_SETDESKWALLPAPER, 
                abs_path, 
                win32con.SPIF_UPDATEINIFILE | win32con.SPIF_SENDCHANGE
            )
            
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 壁纸已更新: {abs_path}")
            return True
        except Exception as e:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 设置壁纸失败: {e}")
            return False
    else:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 文件不存在: {abs_path}")
        return False

def create_task_scheduler():
    """创建任务计划程序，在用户登录时启动本程序"""
    try:
        # 获取当前Python脚本的绝对路径
        script_path = abspath(__file__)
        
        # 如果被打包成exe，使用sys.executable
        if getattr(sys, 'frozen', False):
            exe_path = sys.executable
        else:
            exe_path = sys.executable
            script_path = f'"{exe_path}" "{script_path}"'
        
        # 创建任务计划程序
        scheduler = win32com.client.Dispatch('Schedule.Service')
        scheduler.Connect()
        
        # 获取任务根文件夹
        root_folder = scheduler.GetFolder('\\')
        
        # 任务名称（使用程序名）
        task_name = 'AutoWallpaperChanger'
        
        # 检查任务是否已存在
        try:
            existing_task = root_folder.GetTask(task_name)
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 任务计划已存在")
            return True
        except:
            pass  # 任务不存在，继续创建
        
        # 创建任务定义
        task_def = scheduler.NewTask(0)
        
        # 创建触发器（用户登录时）
        trigger = task_def.Triggers.Create(9)  # TASK_TRIGGER_LOGON = 9
        trigger.Id = 'LogonTrigger'
        trigger.UserId = win32api.GetUserName()
        
        # 创建操作（运行程序）
        action = task_def.Actions.Create(0)  # TASK_ACTION_EXEC = 0
        if getattr(sys, 'frozen', False):
            action.Path = exe_path
            action.WorkingDirectory = dirname(exe_path)
        else:
            action.Path = exe_path
            action.Arguments = script_path
            action.WorkingDirectory = dirname(script_path)
        
        # 设置任务属性
        task_def.RegistrationInfo.Description = '自动检测并更换壁纸程序'
        task_def.Settings.Enabled = True
        task_def.Settings.Hidden = False
        task_def.Settings.RunOnlyIfIdle = False
        task_def.Settings.StopIfGoingOnBatteries = False
        task_def.Settings.DisallowStartIfOnBatteries = False
        task_def.Settings.StartWhenAvailable = True
        task_def.Principal.RunLevel = 1  # TASK_RUNLEVEL_HIGHEST
        
        # 注册任务
        root_folder.RegisterTaskDefinition(
            task_name,
            task_def,
            6,  # TASK_CREATE_OR_UPDATE
            None,
            None,
            3   # TASK_LOGON_PASSWORD
        )
        
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 任务计划程序已创建")
        return True
        
    except Exception as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 创建任务计划失败: {e}")
        return False

def main():
    """主函数"""
    print("=" * 50)
    print("自动壁纸检测与修复程序")
    print("功能：每分钟检测注册表中的壁纸路径是否与w.txt中的一致")
    print("如果不一致，自动修复为w.txt中的路径")
    print("=" * 50)
    
    # 首次运行时创建任务计划
    if not os.path.exists("task_created.flag"):
        try:
            if create_task_scheduler():
                # 创建标记文件，避免重复创建任务
                with open("task_created.flag", "w") as f:
                    f.write("1")
        except Exception as e:
            print(f"创建任务计划时出错: {e}")
    
    # 读取目标壁纸路径
    target_wallpaper_path = get_target_wallpaper_path()
    
    if target_wallpaper_path:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 目标壁纸路径: {target_wallpaper_path}")
    else:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 警告: 未找到w.txt文件或文件内容为空")
        target_wallpaper_path = ""
    
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始监控注册表壁纸路径...")
    print("按 Ctrl+C 退出程序")
    
    try:
        while True:
            time.sleep(60)  # 等待60秒
            
            # 从注册表读取当前壁纸路径
            current_wallpaper_path = get_current_wallpaper_from_registry()
            
            if current_wallpaper_path and target_wallpaper_path:
                # 标准化路径进行比较
                current_normalized = abspath(current_wallpaper_path)
                target_normalized = abspath(target_wallpaper_path)
                
                if current_normalized.lower() != target_normalized.lower():
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 检测到壁纸路径不一致")
                    print(f"  注册表路径: {current_normalized}")
                    print(f"  目标路径: {target_normalized}")
                    print(f"  正在修复...")
                    
                    # 修复壁纸路径
                    if set_wallpaper(target_wallpaper_path):
                        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 壁纸已修复为目标路径")
                    else:
                        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 壁纸修复失败")
                else:
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 壁纸路径一致，无需更改")
            elif not current_wallpaper_path:
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 无法从注册表读取壁纸路径")
            elif not target_wallpaper_path:
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] w.txt中没有有效的壁纸路径")
                    
    except KeyboardInterrupt:
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 程序已停止")
    except Exception as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 程序出错: {e}")

if __name__ == "__main__":
    # 检查是否是首次运行
    print("壁纸监控程序启动")
    
    try:
        main()
    except Exception as e:
        print(f"程序运行出错: {e}")
        input("按回车键退出...")
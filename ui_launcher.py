import tkinter as tk
from tkinter import ttk, messagebox
import threading
import ctypes
from ctypes import wintypes
import time

user32 = ctypes.windll.user32

# 窗口枚举回调函数（用于查找所有 WorkerW）
def _enum_windows_proc(hwnd, lParam):
    class_name = ctypes.create_unicode_buffer(256)
    user32.GetClassNameW(hwnd, class_name, 256)
    if class_name.value == "WorkerW":
        # 将找到的 WorkerW 句柄添加到列表
        workerw_list.append(hwnd)
    return True

# 获取屏幕分辨率
def _get_screen_size():
    return user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)

# 主函数：将指定窗口嵌入桌面图标下层
def _embed_window_as_wallpaper(target_hwnd):
    # 1. Validate target window handle
    if not user32.IsWindow(target_hwnd):
        print("[ERROR]Target window handle is invalid or no longer exists.")
        return False

    # 2. Get Progman window handle
    progman = user32.FindWindowW("Progman", "Program Manager")
    if not progman:
        print("[ERROR]Failed to find Progman window.")
        return False
    print(f"[DEBUG]Found Progman: 0x{progman:X}")

    # 3. Send 0x052C message to trigger WorkerW creation
    user32.SendMessageW(progman, 0x052C, 0, 0)
    print("[DEBUG]Sent 0x052C message to trigger desktop structure update")

    # Wait briefly for system to create windows
    time.sleep(0.1)

    # 4. Enumerate all WorkerW windows
    global workerw_list
    workerw_list = []
    ENUMWNDPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    user32.EnumWindows(ENUMWNDPROC(_enum_windows_proc), 0)

    if len(workerw_list) < 2:
        print("[ERROR]Insufficient WorkerW windows found; expected at least 2.")
        return False
    print(f"[DEBUG]Found {len(workerw_list)} WorkerW window(s)")

    # 5. Locate the WorkerW that contains SHELLDLL_DefView (desktop icons container)
    shell_defview_container = None
    for workerw in workerw_list:
        if not user32.IsWindow(workerw):
            continue  # Skip invalid handles
        defview = user32.FindWindowExW(workerw, None, "SHELLDLL_DefView", None)
        if defview:
            shell_defview_container = workerw
            print(f"[DEBUG]Found icon container WorkerW: 0x{workerw:X}")
            break

    if not shell_defview_container:
        print("[ERROR]Could not locate WorkerW containing SHELLDLL_DefView.")
        return False

    # 6. Find the next WorkerW after the icon container (this one overlays the wallpaper)
    try:
        idx = workerw_list.index(shell_defview_container)
        if idx + 1 >= len(workerw_list):
            print("[DEBUG]Subsequent WorkerW has been removed.")
        else:
            candidate_workerw = workerw_list[idx + 1]

            if not user32.IsWindow(candidate_workerw):
                print("[WARNING]Candidate overlay WorkerW is no longer valid.")
                # Proceed anyway; it might have been destroyed by system
            else:
                print(f"[DEBUG]Candidate overlay WorkerW: 0x{candidate_workerw:X}")

                # Optional verification: next window after candidate should be Progman
                next_after_candidate = user32.GetWindow(candidate_workerw, 2)  # GW_HWNDNEXT
                if next_after_candidate != progman:
                    print("[WARNING]Candidate WorkerW is not followed by Progman; topology may have changed.")
                else:
                    print("[DEBUG]Topology verified: candidate WorkerW is correctly positioned.")

                # Close the overlay WorkerW
                print(f"[DEBUG]Closing overlay WorkerW: 0x{candidate_workerw:X}")
                user32.SendMessageW(candidate_workerw, 0x0010, 0, 0)  # WM_CLOSE

    except (ValueError, IndexError):
        print("[ERROR]Unexpected error locating candidate WorkerW.")
        return False

    # 7. Reparent target window under Progman
    if user32.SetParent(target_hwnd, progman):
        print(f"[DEBUG]Successfully reparented window 0x{target_hwnd:X} under Progman")

        screen_size = _get_screen_size()
        # Adjust position and size (optional)
        user32.SetWindowPos(
            target_hwnd,
            -1,          # HWND_BOTTOM
            0, 0,        # x, y
            *screen_size,  # width, height (adjust per monitor if needed)
            0x0040 | 0x0001  # SWP_NOZORDER | SWP_NOREDRAW
        )
        return True
    else:
        print("[ERROR]SetParent failed; could not embed window under desktop.")
        return False

# ================== 使用示例 ==================

# 示例：查找一个已知窗口并嵌入
def set_background_layer(window_title):
    target = user32.FindWindowW(None, window_title)
    if not target:
        print(f"[ERROR]Window with title '{window_title}' not found")
    else:
        print(f"[DEBUG]Found target window: 0x{target:X}")
        success = _embed_window_as_wallpaper(target)
        if success:
            print("[DEBUG]Embedding succeeded! Window is now displayed as desktop wallpaper below icons.")
        else:
            print("[ERROR]Embedding failed.")

def cancel_background_layer(window_title):
    progman = user32.FindWindowW("Progman", "Program Manager")
    target = user32.FindWindowExW(progman, None, 'SDL_app', window_title)
    if not target:
        print(f"[ERROR]Window with title '{window_title}' not found under Progman")
    else:
        print(f"[DEBUG]Found target window: 0x{target:X}")
        if user32.SetParent(target, None):
            print("[DEBUG]Successfully canceled background layer (window detached from Progman).")
        else:
            print("[ERROR]Failed to cancel background layer (SetParent failed).")


class WallpaperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("桌面壁纸层控制器")
        self.root.geometry("400x220")
        self.root.resizable(False, False)

        # --- 标题 ---
        title_label = ttk.Label(root, text="Windows 桌面壁纸嵌入工具", font=("Microsoft YaHei", 16, "bold"))
        title_label.pack(pady=10)

        # --- 输入框区域 ---
        frame = ttk.Frame(root)
        frame.pack(pady=10, padx=20, fill="x")

        ttk.Label(frame, text="目标窗口标题:").pack(anchor="w")
        
        # 这里填入窗口的标题，例如 "vlc" 或 "无标题 - 记事本"
        self.entry_var = tk.StringVar(value="") 
        self.entry = ttk.Entry(frame, textvariable=self.entry_var, font=("Consolas", 10))
        self.entry.pack(fill="x", pady=5)
        self.entry.focus()

        # --- 按钮区域 ---
        btn_frame = ttk.Frame(root)
        btn_frame.pack(pady=20)

        # 设置为壁纸按钮 (绿色)
        self.set_btn = ttk.Button(btn_frame, text="设置为壁纸层 (Set Background)", command=self.start_set_process)
        self.set_btn.pack(side="left", padx=10)

        # 取消壁纸层按钮 (红色/橙色)
        self.cancel_btn = ttk.Button(btn_frame, text="取消壁纸层 (Cancel)", command=self.start_cancel_process)
        self.cancel_btn.pack(side="left", padx=10)

        # --- 状态栏 ---
        self.status_var = tk.StringVar(value="就绪")
        self.status_bar = ttk.Label(root, textvariable=self.status_var, relief="sunken", anchor="w")
        self.status_bar.pack(side="bottom", fill="x")

    def start_set_process(self):
        """启动设置壁纸的线程"""
        title = self.entry_var.get().strip()
        if not title:
            messagebox.showwarning("输入错误", "请输入目标窗口的标题！")
            return
        # 防止界面卡死，使用线程
        thread = threading.Thread(target=self._run_set, args=(title,), daemon=True)
        thread.start()

    def start_cancel_process(self):
        """启动取消壁纸的线程"""
        title = self.entry_var.get().strip()
        if not title:
            messagebox.showwarning("输入错误", "请输入目标窗口的标题！")
            return
        thread = threading.Thread(target=self._run_cancel, args=(title,), daemon=True)
        thread.start()

    def _run_set(self, title):
        """实际调用核心脚本的 set_background_layer 函数"""
        try:
            self.status_var.set(f"正在尝试将窗口 '{title}' 嵌入桌面...")
            self.root.update_idletasks() # 强制刷新界面显示状态
            
            # 调用你脚本里的函数
            set_background_layer(title)
            
            self.status_var.set("操作完成：窗口已尝试嵌入桌面。")
            messagebox.showinfo("成功", f"已尝试将窗口 '{title}' 设置为桌面壁纸层。")
        except Exception as e:
            error_msg = str(e)
            self.status_var.set(f"发生错误: {error_msg}")
            messagebox.showerror("错误", f"操作失败: {error_msg}")

    def _run_cancel(self, title):
        """实际调用核心脚本的 cancel_background_layer 函数"""
        try:
            self.status_var.set(f"正在尝试恢复窗口 '{title}'...")
            self.root.update_idletasks()
            
            # 调用你脚本里的函数
            cancel_background_layer(title)
            
            self.status_var.set("操作完成：窗口已尝试从桌面层移除。")
            messagebox.showinfo("成功", f"已尝试取消窗口 '{title}' 的桌面壁纸层。")
        except Exception as e:
            error_msg = str(e)
            self.status_var.set(f"发生错误: {error_msg}")
            messagebox.showerror("错误", f"操作失败: {error_msg}")

if __name__ == "__main__":
    root = tk.Tk()
    app = WallpaperApp(root)
    root.mainloop()
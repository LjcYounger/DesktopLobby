from PySide6.QtWidgets import QMessageBox
def repeat_confirm(times: int):
    for x in range(times):
        msg=QMessageBox.question(None, "提示", "你确定要运行这个程序吗？"+"真的吗？"*x, QMessageBox.Yes|QMessageBox.No)
        if msg == QMessageBox.No:
            return False
    return True
        
    
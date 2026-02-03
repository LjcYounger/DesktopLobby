from io import BytesIO
from PIL import Image
from PySide6.QtCore import QBuffer, QIODevice
from PySide6.QtGui import QImage, QPixmap

def fromqimage(qimage):
    """
    将QImage转换为PIL Image
    """
    buffer = QBuffer()
    buffer.open(QIODevice.ReadWrite)
    
    # 根据是否有alpha通道选择保存格式
    if qimage.hasAlphaChannel():
        qimage.save(buffer, "PNG")
    else:
        qimage.save(buffer, "PPM")
    
    # 读取数据并转换为PIL Image
    buffer.seek(0)
    pil_image = Image.open(BytesIO(buffer.readAll().data()))
    buffer.close()
    
    return pil_image

def toqpixmap(pil_image):
    """
    将PIL Image转换为QPixmap
    """
    if pil_image.mode != 'RGBA':
        pil_image = pil_image.convert('RGBA')
    
    # 使用PIL的tobytes方法获取数据
    data = pil_image.tobytes('raw', 'BGRA')
    width, height = pil_image.size
    
    qimage = QImage(data, width, height, QImage.Format_ARGB32)
    return QPixmap.fromImage(qimage)
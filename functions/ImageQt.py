import numpy as np
from PIL import Image
from PySide6.QtGui import QImage, QPixmap
def toqpixmap(pil_image: Image.Image) -> QPixmap:

    if pil_image.mode != 'RGBA':
        pil_image = pil_image.convert('RGBA')
    
    data = np.array(pil_image)
    h, w, c = data.shape
    qimage = QImage(data.data, w, h, c*w, QImage.Format_RGBA8888)
    return QPixmap.fromImage(qimage)
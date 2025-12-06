from PIL import Image
import numpy as np
from scipy import ndimage

def removeRemoteImage(image0, startx, starty, minAlpha=5):
    if image0.mode != 'RGBA':
        image0 = image0.convert('RGBA')
    
    alpha = np.array(image0)[:, :, 3]
    mask = alpha >= minAlpha
    
    # 标记所有连通区域
    labels, num_labels = ndimage.label(mask)
    target_label = labels[starty, startx]
    
    if target_label == 0:  # 起点 Alpha 不足
        return Image.new('RGBA', image0.size, (0,0,0,0))
    
    # 提取该区域
    region_mask = (labels == target_label)
    new_array = np.zeros((*image0.size[::-1], 4), dtype=np.uint8)
    new_array[region_mask] = np.array(image0)[region_mask]
    
    return Image.fromarray(new_array, 'RGBA')

if __name__  == '__main__':
    from PIL import Image
    import time
    i = Image.open('CH0069_spr.png')
    t = time.perf_counter()
    r = removeRemoteImage(i, 512, 1024)
    t1 = time.perf_counter()
    print(t1-t)
    r.save('r.png')
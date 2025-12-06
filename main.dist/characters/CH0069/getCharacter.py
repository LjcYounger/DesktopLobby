import re
from json import loads
import ast
import os
from removeRemoteImage import *

def getCharacter(name):

    with open(f"characters/{name}/{name}_spr.atlas.txt", 'r') as txt:
        content = txt.readlines()
    orimage = Image.open(f"characters/{name}/{name}_spr.png").convert("RGBA")
    orisize = ast.literal_eval(content[2][(content[2].find(':') + 2) :])

    regionRRIstart={'CH0069': (600, 136), 'CH00691': (590, 93), 'CH00692': (310, 30)}
    sources={}
    for a in range(6, len(content) - 6, 7):
        partname=content[a][:-1]
        xy = ast.literal_eval(content[a + 2][(content[a + 2].find(':') + 2) :])
        size = ast.literal_eval(content[a + 3][(content[a + 3].find(':') + 2) :])
        x, y, w, h = xy[0], xy[1], size[0], size[1]
        if content[a + 1][content[a + 1].find(':') + 2 :] == 'true\n':
            region = orimage.crop((x, y, x + h, y + w))
            region = region.rotate(-90, expand=True)
        elif content[a + 1][content[a + 1].find(':') + 2 :] == '180\n':
            region = orimage.crop((x, y, x + w, y + h))
            region = region.rotate(-180, expand=True)
        elif content[a + 1][content[a + 1].find(':') + 2 :] == '270\n':
            region = orimage.crop((x, y, x + h, y + w))
            region = region.rotate(-270, expand=True)
        else:
            region = orimage.crop((x, y, x + w, y + h))

        if partname == 'Halo':
            partname=partname.lower()
            region.paste(Image.new("RGBA", (145, 58)), (0, 0))
        elif partname in regionRRIstart.keys():
            tempfolderPath=os.path.join(os.getenv('TEMP'), 'DesktopLobby', name.upper())
            os.makedirs(tempfolderPath, exist_ok=True)
            path=os.path.join(tempfolderPath, f"{partname}.png")
            if os.path.exists(path):
                region=Image.open(path)
            else:
                region=removeRemoteImage(region, regionRRIstart[partname][0], regionRRIstart[partname][1])
                region.save(path)
        sources[partname]=region
    with open(f"characters/{name}/settings.json", 'r') as txt:
        content = ''.join([s for s in txt.readlines() if not s.startswith('#')])
        settings=loads(content)

    image0=Image.new("RGBA", (1013, 1490))
    image0.paste(sources['CH0069'], (0, 0))
    image0.paste(sources['CH00691'], (0, 642), sources['CH00691'])
    image0.paste(sources['CH00692'], (282, 1001), sources['CH00692'])
    pictures={}
    targetalpha=image0.split()[-1]
    emotionpos=settings['emotions']
    for key in sources.keys():
        if re.match(r'^\d\d', key) or key == 'eyeclose':
            image=image0.copy()
            emotionpos=settings.get(key, settings['emotions'])
            image.paste(sources[key], (emotionpos[0]-sources[key].width, emotionpos[1]-sources[key].height), sources[key])
            image=Image.merge('RGBA', image.split()[:3] + tuple([targetalpha]))
            pictures[key]=image
    pictures['halo']=sources['halo']
    
    return pictures, settings

if __name__=='__main__':
    p, s =getCharacter('CH0069')
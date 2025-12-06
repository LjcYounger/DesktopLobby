import re
from PIL import Image
from json import loads
import ast
import os.path
from removeRemoteImage import *

def getCharacter(name):

    with open(f"characters/{name}/{name}_spr.atlas.txt", 'r') as txt:
        content = txt.readlines()
    orimage = Image.open(f"characters/{name}/{name}_spr.png").convert("RGBA")
    orisize = ast.literal_eval(content[1][(content[1].find(':') + 1) :])

    sources={}
    nameindex=[]
    for a in range(4, len(content)):
        if not any(content[a].startswith(x) for x in ['bounds', 'offsets', 'rotate']):
            nameindex.append(a)
    nameindex.append(len(content))
    for b in range(0, len(nameindex)-1):
        rotate=0
        for c in range(nameindex[b]+1, nameindex[b+1]):
            if content[c].startswith('bounds'):
                x, y, w, h = ast.literal_eval(content[c][(content[c].find(':') + 1) :])
            elif content[c].startswith('rotate'):
                rotate = int(content[c][(content[c].find(':') + 1) :])
        if rotate==90:
            region = orimage.crop((x, y, x + h, y + w))
            region = region.rotate(-90, expand=True)
        else:
            region = orimage.crop((x, y, x + w, y + h))
        if content[nameindex[b]].replace('\n', '') == name:
            tempfolderPath=os.path.join(os.getenv('TEMP'), 'DesktopLobby', name)
            os.makedirs(tempfolderPath, exist_ok=True)
            path=os.path.join(tempfolderPath, f"{name}.png")
            if os.path.exists(path):
                region=Image.open(path)
            else:
                region=removeRemoteImage(region, 25, 289)
                region.save(path)
        sources[content[nameindex[b]].replace('\n', '')]=region
    
    with open(f"characters/{name}/settings.json", 'r') as txt:
        content = ''.join([s for s in txt.readlines() if not s.startswith('#')])
        settings=loads(content)

    pictures={}
    image0=sources[name]
    targetalpha=image0.split()[-1]
    for key in sources.keys():
        if re.match(r'^\d\d', key) or key == 'eyeclose' or key == 'default':
            image=image0.copy()
            image.paste(sources[key], settings[key[:2]], sources[key])
            image.paste(sources['Hair_Cover_01'], settings["Hair_Cover_01"], sources['Hair_Cover_01'])
            image=Image.merge('RGBA', image.split()[:3] + tuple([targetalpha]))
            pictures[key]=image
    
    #for k, i in sources.items():
    #    i.save(f"{k}.png")
    pictures['halo']=sources['halo']
    return pictures, settings

if __name__=='__main__':
    p, s =getCharacter('momoi')
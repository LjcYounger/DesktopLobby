import re
from PIL import Image
from json import loads
import ast

def getCharacter(name):
    with open(f"characters/{name}/{name}_spr.atlas.txt", 'r') as txt:
        content = txt.readlines()
    orimage = Image.open(f"characters/{name}/{name}_spr.png").convert("RGBA")
    orisize = ast.literal_eval(content[2][(content[2].find(':') + 2) :])

    sources={}
    for a in range(6, len(content) - 6, 7):
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
        sources[content[a][:-1]]=region
    
    with open(f"characters/{name}/settings.json", 'r') as txt:
        content = ''.join([s for s in txt.readlines() if not s.startswith('#')])
        settings=loads(content)

    pictures={}
    image0=sources[name]
    targetalpha=image0.split()[-1]
    emotionpos=settings['emotions']
    for key in sources.keys():
        if re.match(r'^\d\d', key) or key == 'eyeclose':
            image=image0.copy()
            image.paste(sources[key], (emotionpos[0], emotionpos[1]-sources[key].size[1]), sources[key])
            image.paste(sources['object_fronthair'], settings['object_fronthair'], sources['object_fronthair'])
            image=Image.merge('RGBA', image.split()[:3] + tuple([targetalpha]))
            pictures[key]=image
    
    halo=sources['halo 1']
    halo.paste(sources['halo 2'], settings['halo 2'], sources['halo 2'])
    halo.paste(sources['halo 3'], settings['halo 3'], sources['halo 3'])
    pictures['halo']=halo
    return pictures, settings
from getResources import getImage
from functions.json_ import load_json
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from itertools import chain
DBInf=load_json("images/Lobby_balloon.json")

font=ImageFont.truetype("fonts/有爱魔兽圆体-R.ttf", 45)
image0 = getImage('Common', 'Lobby_balloon')
def textsize(draw, text, font=None):
    bbox=draw.textbbox((0,0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]

def render_Lobby_balloonCombined(textlines, line_spacing=4):
    textlines = list(chain(*[line.split('\n') for line in textlines]))
    orimage = image0.copy()
    draw=ImageDraw.Draw(orimage)
    standardSize = textsize(draw, "羊", font)
    standardSize = (standardSize[0], standardSize[1] + line_spacing)

    dbPlusW = max(textsize(draw, a, font)[0] for a in textlines)
    dbPlusH = (len(textlines) -1) * standardSize[1]
    newimage = Image.new(orimage.mode, (orimage.size[0]+dbPlusW, orimage.size[1]+dbPlusH))
    newimage.paste(orimage.crop((0, 0, 82, orimage.size[0])), (0, 0))
    newimage.paste(orimage.crop((82, 0, orimage.size[0], orimage.size[1])), (82+dbPlusW, 0))

    verticalLine = orimage.crop((82, 0, 83, orimage.size[1]))
    for a in range(0, dbPlusW):
        newimage.paste(verticalLine, (82+a, 0))
    
    if dbPlusH != 0:
        orimage = newimage
        newimage.paste(orimage.crop((0, 0, orimage.size[1], 86)), (0, 0))
        newimage.paste(orimage.crop((0, 86, orimage.size[0], orimage.size[1])), (0, 86+dbPlusH))
        horizontalLine = orimage.crop((0, 86, orimage.size[0], 87))
        for a in range(0, dbPlusH):
            newimage.paste(horizontalLine, (0, 86+a))
    alpha=newimage.split()[-1]
    draw=ImageDraw.Draw(newimage)
    for a, text in enumerate(textlines):
        draw.text((78, 34 + a*standardSize[1]), text, font=font, fill=(0, 0, 0))
    newimage=Image.merge('RGBA', newimage.split()[:3] + tuple([alpha]))
    newimage=newimage.resize(tuple(int(x*DBInf['k']) for x in newimage.size))
    print("[DEBUG]Dialog Content:", textlines)
    return newimage
def render_Lobby_balloon(textlines, line_spacing=4):
    textlines = list(chain(*[line.split('\n') for line in textlines]))

    orimage = image0.copy()
    draw=ImageDraw.Draw(orimage)
    standardSize = textsize(draw, "羊", font)
    standardSize = (standardSize[0], standardSize[1] + line_spacing)

    dbPlusW = max(textsize(draw, a, font)[0] for a in textlines)
    dbPlusH = (len(textlines) -1) * standardSize[1]
    newimage = Image.new(orimage.mode, (orimage.size[0]+dbPlusW, orimage.size[1]+dbPlusH))
    newimage.paste(orimage.crop((0, 0, 82, orimage.size[0])), (0, 0))
    newimage.paste(orimage.crop((82, 0, orimage.size[0], orimage.size[1])), (82+dbPlusW, 0))

    verticalLine = orimage.crop((82, 0, 83, orimage.size[1]))
    for a in range(0, dbPlusW):
        newimage.paste(verticalLine, (82+a, 0))
    
    if dbPlusH != 0:
        orimage = newimage
        newimage.paste(orimage.crop((0, 0, orimage.size[1], 86)), (0, 0))
        newimage.paste(orimage.crop((0, 86, orimage.size[0], orimage.size[1])), (0, 86+dbPlusH))
        horizontalLine = orimage.crop((0, 86, orimage.size[0], 87))
        for a in range(0, dbPlusH):
            newimage.paste(horizontalLine, (0, 86+a))
    textimage=Image.new(newimage.mode, newimage.size)
    draw=ImageDraw.Draw(textimage)
    for a, text in enumerate(textlines):
        draw.text((78, 34 + a*standardSize[1]), text, font=font, fill=(0, 0, 0))
    alphan=np.array(newimage)[:, :, 3]
    arrt=np.array(textimage)
    alphat=arrt[:, :, 3]
    mask=alphat != 0
    alphat[mask]=alphan[mask]
    textimage=Image.fromarray(arrt)

    newimage=newimage.resize(tuple(int(x*DBInf['k']) for x in newimage.size))
    textimage=textimage.resize(tuple(int(x*DBInf['k']) for x in textimage.size))
    print(f"[DEBUG]Dialog Content: {textlines}")
    return newimage, textimage
if __name__ == "__main__":
    i = render_Lobby_balloonCombined(['计划客户端结婚登记\n计划几号放假', '很简单较好的\n寒假\nfd'])
    i.save(f'1.png')
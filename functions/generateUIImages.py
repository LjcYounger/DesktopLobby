from PIL import Image, ImageDraw, ImageFont
import numpy as np
from getResources import getImage

def generateImage(type, num=2):
    if type== "HideDesktopIcons":
        shell0=getImage('Common', 'Common_BGDeco')
        cores=[getImage('Common', 'Common_UIHide_Icon'),getImage('Common', 'Common_UIHide_Icon2')]

        shell=Image.new("RGBA", (shell0.width*2-10, shell0.height), (0, 0, 0, 0))
        shell.paste(shell0, (0, 0))
        shell.paste(shell0.rotate(180), (shell0.width-10, 0))
        draw=ImageDraw.Draw(shell)
        draw.rectangle([(25, 0), (152, 99)], fill=(255, 255, 255, 255))
        outputs=[]
        for core in cores:
            array=np.array(core)
            array[:,:,:3]=[69,99,151]
            array=array.astype(np.uint8)
            core=Image.fromarray(array)
            output=shell.copy()
            output.paste(core, tuple(int((x-y)/2) for x, y in zip(shell.size, core.size)), mask=core)
            outputs.append(output)
        return outputs
    elif type == "ChangeCharacterMode":
        shell0=getImage('Common', 'Common_BGDeco')
        core=getImage('Common', 'Common_Icon_Change')
        core=core.resize(tuple(int(1.6*x) for x in core.size))

        shell=Image.new("RGBA", (shell0.width*2-10, shell0.height), (0, 0, 0, 0))
        shell.paste(shell0, (0, 0))
        shell.paste(shell0.rotate(180), (shell0.width-10, 0))
        draw=ImageDraw.Draw(shell)
        draw.rectangle([(25, 0), (152, 99)], fill=(255, 255, 255, 255))

        array=np.array(core)
        array[:,:,:3]=[69,99,151]
        array=array.astype(np.uint8)
        core=Image.fromarray(array)
        shell.paste(core, tuple(int((x-y)/2) for x, y in zip(shell.size, core.size)), mask=core)

        font=ImageFont.truetype("fonts/有爱魔兽圆体-R.ttf", 30)
        outputs=[]
        for n in range(1, num+1):
            output=shell.copy()
            draw=ImageDraw.Draw(output)
            text=f"{n}/{num}"
            textsize=draw.textsize(text, font)
            draw.text(tuple(int((x-y)/2) for x, y in zip(output.size, textsize)), text, fill=(69,99,151), font=font)
            outputs.append(output)
        return outputs
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont
from flask import send_file

from assets.utils import http

from assets.utils.textutils import auto_text_size, render_text_with_emoji



class WhoThisIs():
    params = ['avatar0', 'text']

    def generate(self, avatars, text, usernames, kwargs):
        base = Image.open(('assets/assets/whothisis/whothisis.bmp'))
        avatar = http.get_image(avatars[0]).resize((215, 215)).convert('RGBA')
        font = ImageFont.truetype('assets/assets/fonts/arimobold.ttf', size=40)
        base.paste(avatar, (523, 15), avatar)
        base.paste(avatar, (509, 567), avatar)
        base = base.convert('RGBA')

        canv = ImageDraw.Draw(base)
        render_text_with_emoji(base, canv, (545, 465), text, font=font, fill='White')

        b = BytesIO()
        base.save(b, format='png')
        b.seek(0)
        return b

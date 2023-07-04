from io import BytesIO

from PIL import Image, ImageDraw, ImageFont
from flask import send_file

from assets.utils import http

from assets.utils.textutils import wrap, render_text_with_emoji



class Floor():
    params = ['avatar0', 'text']

    def generate(self, avatars, text, usernames, kwargs):
        base = Image.open(('assets/assets/floor/floor.bmp')).convert('RGBA')
        avatar = http.get_image(avatars[0]).resize((45, 45)).convert('RGBA')
        avatar2 = avatar.copy().resize((23, 23))
        font = ImageFont.truetype('assets/assets/fonts/sans.ttf', size=22)
        canv = ImageDraw.Draw(base)

        text = wrap(font, text, 300)
        render_text_with_emoji(base, canv, (168, 36), text, font=font, fill='Black')

        base.paste(avatar, (100, 90), avatar)
        base.paste(avatar2, (330, 90), avatar2)
        base = base.convert('RGBA')

        b = BytesIO()
        base.save(b, format='png')
        b.seek(0)
        return b

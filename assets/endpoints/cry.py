from io import BytesIO

from PIL import Image, ImageDraw, ImageFont
from flask import send_file


from assets.utils.textutils import wrap, render_text_with_emoji



class Cry():
    params = ['text']

    def generate(self, avatars, text, usernames, kwargs):
        base = Image.open(('assets/cry/cry.bmp'))
        font = ImageFont.truetype('assets/fonts/tahoma.ttf', size=20)
        canv = ImageDraw.Draw(base)

        text = wrap(font, text, 180)
        render_text_with_emoji(base, canv, (382, 80), text, font=font, fill='Black')

        b = BytesIO()
        base.save(b, format='jpeg')
        b.seek(0)
        return send_file(b, mimetype='image/jpeg')

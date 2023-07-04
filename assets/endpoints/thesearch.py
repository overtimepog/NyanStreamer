from io import BytesIO

from PIL import Image, ImageDraw, ImageFont
from flask import send_file


from assets.utils.textutils import wrap, render_text_with_emoji



class TheSearch():
    params = ['text']

    def generate(self, avatars, text, usernames, kwargs):
        base = Image.open(('assets/search/thesearch.bmp')).convert('RGBA')
        font = ImageFont.truetype('assets/fonts/sans.ttf', size=16)
        canv = ImageDraw.Draw(base)

        text = wrap(font, text, 178)
        render_text_with_emoji(base, canv, (65, 335), text, font=font, fill='Black')
        base = base.convert('RGB')

        b = BytesIO()
        base.save(b, format='jpeg')
        b.seek(0)
        return send_file(b, mimetype='image/jpeg')

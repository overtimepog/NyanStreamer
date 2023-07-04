from io import BytesIO

from PIL import Image, ImageDraw, ImageFont
from flask import send_file


from assets.utils.textutils import wrap, render_text_with_emoji



class Piccolo():
    params = ['text']

    def generate(self, avatars, text, usernames, kwargs):
        base = Image.open(('assets/piccolo/piccolo.bmp'))
        font = ImageFont.truetype('assets/fonts/medium.woff', size=33)
        canv = ImageDraw.Draw(base)
        text = wrap(font, text, 850)
        render_text_with_emoji(base, canv, (5, 5), text[:300], font=font, fill='Black')

        base = base.convert('RGB')
        b = BytesIO()
        base.save(b, format='jpeg')
        b.seek(0)
        return send_file(b, mimetype='image/jpeg')

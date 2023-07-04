from io import BytesIO

from PIL import Image, ImageDraw, ImageFont
from flask import send_file


from assets.utils.textutils import wrap, render_text_with_emoji



class Presentation():
    params = ['text']

    def generate(self, avatars, text, usernames, kwargs):
        base = Image.open(('assets/assets/presentation/presentation.bmp'))
        font = ImageFont.truetype('assets/assets/fonts/verdana.ttf', size=24)
        canv = ImageDraw.Draw(base)
        text = wrap(font, text, 330)
        render_text_with_emoji(base, canv, (150, 80), text, font=font, fill='Black')

        base = base.convert('RGB')
        b = BytesIO()
        base.save(b, format='jpeg')
        b.seek(0)
        return send_file(b, mimetype='image/jpeg')

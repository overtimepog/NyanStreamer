from io import BytesIO

from PIL import Image, ImageDraw, ImageFont
from flask import send_file


from assets.utils.textutils import wrap, render_text_with_emoji



class ExcuseMe():
    params = ['text']

    def generate(self, avatars, text, usernames, kwargs):
        base = Image.open(('assets/assets/excuseme/excuseme.bmp'))

        font = ImageFont.truetype('assets/assets/fonts/sans.ttf', size=40)
        canv = ImageDraw.Draw(base)
        text = wrap(font, text, 787)
        render_text_with_emoji(base, canv, (20, 15), text, font=font, fill='Black')

        base = base.convert('RGB')

        b = BytesIO()
        base.save(b, format='jpeg')
        b.seek(0)
        return b

from io import BytesIO

from PIL import Image, ImageDraw, ImageFont
from flask import send_file


from assets.utils.textutils import wrap, render_text_with_emoji



class Walking():
    params = ['text']

    def generate(self, avatars, text, usernames, kwargs):
        base = Image.open(('assets/assets/walking/walking.bmp'))

        font = ImageFont.truetype('assets/assets/fonts/sans.ttf', size=50)
        canv = ImageDraw.Draw(base)
        text = wrap(font, text, 1000)
        render_text_with_emoji(base, canv, (35, 35), text, font=font, fill='black')

        base = base.convert('RGB')

        b = BytesIO()
        base.save(b, format='jpeg')
        b.seek(0)
        return b

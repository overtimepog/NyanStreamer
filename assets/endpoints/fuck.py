from io import BytesIO

from PIL import Image, ImageDraw, ImageFont
from flask import send_file


from assets.utils.textutils import render_text_with_emoji, wrap



class Fuck():
    params = ['text']

    def generate(self, avatars, text, usernames, kwargs):
        text = text.replace(', ', ',').split(',')
        if len(text) != 2:
            text = ['me not using commas', 'you must split the lines with a comma']
        base = Image.open(('assets/assets/fuck/fuck.jpg'))
        font = ImageFont.truetype('assets/assets/fonts/verdana.ttf', size=24)
        canv = ImageDraw.Draw(base)
        render_text_with_emoji(base, canv, (200, 600), wrap(font, text[0], 320), font, 'white')
        render_text_with_emoji(base, canv, (750, 700), wrap(font, text[1], 320), font, 'white')

        base = base.convert('RGB')
        b = BytesIO()
        base.save(b, format='jpeg')
        b.seek(0)
        return b

from io import BytesIO

from PIL import Image, ImageDraw, ImageFont
from flask import send_file


from assets.utils.textutils import render_text_with_emoji, wrap



class Lick():
    params = ['text']

    def generate(self, avatars, text, usernames, kwargs):
        text = text.replace(', ', ',').split(',')
        if len(text) != 2:
            text = ['Dank Memer', 'People who do not split with a comma']
        base = Image.open(('assets/lick/lick.jpg'))
        font = ImageFont.truetype('assets/fonts/verdana.ttf', size=24)
        canv = ImageDraw.Draw(base)
        render_text_with_emoji(base, canv, (80, 200), wrap(font, text[0], 220), font, 'white')
        render_text_with_emoji(base, canv, (290, 240), wrap(font, text[1], 320), font, 'white')

        base = base.convert('RGB')
        b = BytesIO()
        base.save(b, format='jpeg')
        b.seek(0)
        return send_file(b, mimetype='image/jpeg')

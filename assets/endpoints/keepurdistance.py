from io import BytesIO

from PIL import Image, ImageDraw, ImageFont
from flask import send_file


from assets.utils.textutils import render_text_with_emoji, wrap



class KeepUrDistance():
    params = ['text']

    def generate(self, avatars, text, usernames, kwargs):
        base = Image.open(('assets/keepurdistance/keepurdistance.png'))
        font = ImageFont.truetype('assets/fonts/MontserratBold.ttf', size=24)
        canv = ImageDraw.Draw(base)

        text = text.upper()

        if len(text) >= 30:
            text  = text[:27] + '...'
        render_text_with_emoji(base, canv, (92, 660), wrap(font, text, 440), font, 'white')

        base = base.convert('RGB')
        b = BytesIO()
        base.save(b, format='jpeg')
        b.seek(0)
        return send_file(b, mimetype='image/jpeg')

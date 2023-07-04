from io import BytesIO

from PIL import Image, ImageDraw, ImageFont
from flask import send_file


from assets.utils.textutils import wrap, render_text_with_emoji



class ViolentSparks():
    params = ['text']

    def generate(self, avatars, text, usernames, kwargs):
        base = Image.open(('assets/violentsparks/violentsparks.bmp'))
        font = ImageFont.truetype('assets/fonts/medium.woff', size=36)
        canv = ImageDraw.Draw(base)
        try:
            me, sparks = text.replace(' ,', ',', 1).split(',', 1)
        except ValueError:
            sparks = 'me'
            me = 'Dank Memer being mad that I forgot to split my text with a comma'
        me = wrap(font, me, 550)
        sparks = wrap(font, sparks, 200)
        render_text_with_emoji(base, canv, (15, 5), me, font=font, fill='White')
        render_text_with_emoji(base, canv, (350, 430), sparks, font=font, fill='Black')

        base = base.convert('RGB')
        b = BytesIO()
        base.save(b, format='jpeg')
        b.seek(0)
        return send_file(b, mimetype='image/jpeg')

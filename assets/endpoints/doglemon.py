from io import BytesIO

from PIL import Image, ImageDraw, ImageFont
from flask import send_file


from assets.utils.textutils import wrap, render_text_with_emoji



class DogLemon():
    params = ['text']

    def generate(self, avatars, text, usernames, kwargs):
        base = Image.open(('assets/doglemon/doglemon.bmp'))
        font = ImageFont.truetype('assets/fonts/medium.woff', size=30)
        canv = ImageDraw.Draw(base)
        try:
            lemon, dog = text.replace(' ,', ',', 1).split(',', 1)
        except ValueError:
            lemon = 'Text that is not seperated by comma'
            dog = 'Dank Memer'
        lemon = wrap(font, lemon, 450)
        dog = wrap(font, dog, 450)
        render_text_with_emoji(base, canv, (850, 100), lemon[:180], font=font, fill='Black')
        render_text_with_emoji(base, canv, (500, 100), dog[:200], font=font, fill='White')

        base = base.convert('RGB')
        b = BytesIO()
        base.save(b, format='jpeg')
        b.seek(0)
        return send_file(b, mimetype='image/jpeg')

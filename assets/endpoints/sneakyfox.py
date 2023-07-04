from io import BytesIO

from PIL import Image, ImageDraw, ImageFont
from flask import send_file


from assets.utils.textutils import wrap, render_text_with_emoji



class SneakyFox():
    params = ['text']

    def generate(self, avatars, text, usernames, kwargs):
        base = Image.open(('assets/sneakyfox/sneakyfox.bmp'))
        font = ImageFont.truetype('assets/fonts/arimobold.ttf', size=36)
        canv = ImageDraw.Draw(base)
        try:
            fox, otherthing = text.replace(' ,', ',', 1).split(',', 1)
        except ValueError:
            fox = 'Text that is not split with a comma'
            otherthing = 'the bot'
        fox = wrap(font, fox, 500)
        otherthing = wrap(font, otherthing, 450)
        render_text_with_emoji(base, canv, (300, 350), fox[:180], font=font, fill='Black')
        render_text_with_emoji(base, canv, (670, 120), otherthing[:180], font=font, fill='Black')

        base = base.convert('RGB')
        b = BytesIO()
        base.save(b, format='jpeg')
        b.seek(0)
        return send_file(b, mimetype='image/jpeg')

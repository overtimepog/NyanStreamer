from io import BytesIO

from PIL import Image, ImageDraw, ImageFont
from flask import send_file


from assets.utils.textutils import wrap, render_text_with_emoji



class ConfusedCat():
    params = ['text']

    def generate(self, avatars, text, usernames, kwargs):
        base = Image.open(('assets/confusedcat/confusedcat.bmp'))
        font = ImageFont.truetype('assets/fonts/medium.woff', size=36)
        canv = ImageDraw.Draw(base)
        try:
            ladies, cat = text.replace(' ,', ',', 1).split(',', 1)
        except ValueError:
            ladies = 'Dank Memer'
            cat = 'People who forget to split text with a comma'
        ladies = wrap(font, ladies, 510)
        cat = wrap(font, cat, 510)
        render_text_with_emoji(base, canv, (5, 5), ladies[:100], font=font, fill='Black')
        render_text_with_emoji(base, canv, (516, 5), cat[:100], font=font, fill='Black')

        base = base.convert('RGB')
        b = BytesIO()
        base.save(b, format='jpeg')
        b.seek(0)
        return send_file(b, mimetype='image/jpeg')

from io import BytesIO

from PIL import Image, ImageDraw, ImageFont
from flask import send_file


from assets.utils.textutils import wrap



class ExpandingWWE():
    params = ['text']

    def generate(self, avatars, text, usernames, kwargs):
        base = Image.open(('assets/assets/expandingwwe/expandingwwe.jpg'))
        font = ImageFont.truetype('assets/assets/fonts/verdana.ttf', size=30)

        text = text.replace(', ', ',')

        if len(text.split(',')) < 5:
            a, b, c, d, e = 'you need, five items, for this, command, (split by commas)'.split(',')
        else:
            a, b, c, d, e = text.split(',', 4)

        a, b, c, d, e = [wrap(font, i, 225).strip() for i in [a, b, c, d, e]]

        canvas = ImageDraw.Draw(base)
        canvas.text((5, 5), a, font=font, fill='Black')
        canvas.text((5, 205), b, font=font, fill='Black')
        canvas.text((5, 410), c, font=font, fill='Black')
        canvas.text((5, 620), d, font=font, fill='Black')
        canvas.text((5, 825), e, font=font, fill='Black')

        b = BytesIO()
        base.save(b, format='jpeg')
        b.seek(0)
        return send_file(b, mimetype='image/jpeg')

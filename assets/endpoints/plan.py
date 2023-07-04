from io import BytesIO

from PIL import Image, ImageDraw, ImageFont
from flask import send_file


from assets.utils.textutils import wrap, render_text_with_emoji



class Plan():
    params = ['text']

    def generate(self, avatars, text, usernames, kwargs):
        base = Image.open(('assets/plan/plan.bmp')).convert('RGBA')
        font = ImageFont.truetype('assets/fonts/sans.ttf', size=16)
        canv = ImageDraw.Draw(base)

        words = text.split(', ')

        if len(words) != 3:
            words = ['you need three items for this command',
                     'and each should be split by commas',
                     'Example: pls plan 1, 2, 3']

        words = [wrap(font, w, 120) for w in words]

        a, b, c = words

        render_text_with_emoji(base, canv, (190, 60), a, font=font, fill='Black')
        render_text_with_emoji(base, canv, (510, 60), b, font=font, fill='Black')
        render_text_with_emoji(base, canv, (190, 280), c, font=font, fill='Black')
        render_text_with_emoji(base, canv, (510, 280), c, font=font, fill='Black')
        base = base.convert('RGB')

        b = BytesIO()
        base.save(b, format='jpeg')
        b.seek(0)
        return send_file(b, mimetype='image/jpeg')

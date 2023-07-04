from io import BytesIO

from PIL import Image, ImageDraw, ImageFont
from flask import send_file


from assets.utils.textutils import wrap



class Citation():
    params = ['text']

    def generate(self, avatars, text, usernames, kwargs):
        text = text.replace(', ', ',').split(',')
        if len(text) != 3:
            text = ['M.O.A. CITATION', 'You must have 3 arguments split by comma', 'PENALTY ASSESSED - WRONG IMAGE']
        base = Image.open(('assets/citation/citation.bmp'))
        font = ImageFont.truetype('assets/fonts/bmmini.ttf', size=16)
        canv = ImageDraw.Draw(base)
        text_0 = wrap(font, text[0], 320)
        text_1 = wrap(font, text[1], 320)
        canv.text((20, 10), text_0, font=font)
        canv.text((20, 45), text_1, font=font)
        size = canv.textsize(text[2], font=font)
        new_width = (base.width - size[0]) / 2
        canv.text((new_width, 130), text[2], font=font, align='center')
        base = base.convert('RGB')
        b = BytesIO()
        base.save(b, format='jpeg')
        b.seek(0)
        return send_file(b, mimetype='image/jpeg')

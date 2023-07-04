from io import BytesIO

from PIL import Image, ImageDraw, ImageFont
from flask import send_file


from assets.utils.textutils import wrap, render_text_with_emoji



class Cheating():
    params = ['text']

    def generate(self, avatars, text, usernames, kwargs):
        base = Image.open(('assets/assets/cheating/cheating.bmp'))
        font = ImageFont.truetype('assets/assets/fonts/medium.woff', size=26)
        canv = ImageDraw.Draw(base)
        try:
            me, classmate = text.replace(' ,', ',', 1).split(',', 1)
        except ValueError:
            me = 'aight thx'
            classmate = 'yo dude, you need to split the text with a comma'
        me = wrap(font, me, 150)
        classmate = wrap(font, classmate, 150)
        render_text_with_emoji(base, canv, (15, 300), me[:50], font=font, fill='White')
        render_text_with_emoji(base, canv, (155, 200), classmate[:50], font=font, fill='White')

        base = base.convert('RGB')
        b = BytesIO()
        base.save(b, format='jpeg')
        b.seek(0)
        return send_file(b, mimetype='image/jpeg')

from io import BytesIO

from PIL import Image, ImageDraw, ImageFont
from flask import send_file


from assets.utils.textutils import wrap, render_text_with_emoji



class SlapsRoof():
    params = ['text']

    def generate(self, avatars, text, usernames, kwargs):
        base = Image.open(('assets/assets/slapsroof/slapsroof.bmp'))
        font = ImageFont.truetype('assets/assets/fonts/medium.woff', size=33)
        canv = ImageDraw.Draw(base)
        suffix = ' in it'
        text = wrap(font, text + suffix, 1150)
        render_text_with_emoji(base, canv, (335, 31), text, font=font, fill='Black')

        base = base.convert('RGB')
        b = BytesIO()
        base.save(b, format='jpeg')
        b.seek(0)
        return send_file(b, mimetype='image/jpeg')

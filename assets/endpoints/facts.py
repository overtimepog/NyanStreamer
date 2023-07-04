from io import BytesIO

from PIL import Image, ImageDraw, ImageFont
from flask import send_file


from assets.utils.textutils import wrap, render_text_with_emoji



class Facts():
    params = ['text']

    def generate(self, avatars, text, usernames, kwargs):
        base = Image.open(('assets/facts/facts.bmp'))
        # We need to create an image layer here for the rotation
        text_layer = Image.new('RGBA', base.size)
        font = ImageFont.truetype('assets/fonts/verdana.ttf', size=25)
        canv = ImageDraw.Draw(text_layer)

        text = wrap(font, text, 400)
        render_text_with_emoji(text_layer, canv, (90, 600), text, font=font, fill='Black')
        text_layer = text_layer.rotate(-13, resample=Image.BICUBIC)
        base.paste(text_layer, (0, 0), text_layer)

        b = BytesIO()
        base.save(b, format='jpeg')
        b.seek(0)
        return send_file(b, mimetype='image/jpeg')

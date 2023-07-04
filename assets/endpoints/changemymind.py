from io import BytesIO

from PIL import Image, ImageDraw, ImageFont
from flask import send_file


from assets.utils.textutils import auto_text_size, render_text_with_emoji



class ChangeMyMind():
    params = ['text']

    def generate(self, avatars, text, usernames, kwargs):
        base = Image.open(('assets/changemymind/changemymind.bmp')).convert('RGBA')
        # We need a text layer here for the rotation
        text_layer = Image.new('RGBA', base.size)
        font, text = auto_text_size(text, ImageFont.truetype('assets/fonts/sans.ttf'), 310)
        canv = ImageDraw.Draw(text_layer)

        render_text_with_emoji(text_layer, canv, (290, 300), text, font=font, fill='Black')

        text_layer = text_layer.rotate(23, resample=Image.BICUBIC)

        base.paste(text_layer, (0, 0), text_layer)
        base = base.convert('RGB')

        b = BytesIO()
        base.save(b, format='jpeg')
        b.seek(0)
        return send_file(b, mimetype='image/jpeg')

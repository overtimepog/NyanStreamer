from io import BytesIO

from PIL import Image, ImageDraw, ImageFont
from flask import send_file


from assets.utils.textutils import auto_text_size, render_text_with_emoji



class HumansGood():
    params = ['text']

    def generate(self, avatars, text, usernames, kwargs):
        base = Image.open(('assets/assets/humansgood/humansgood.bmp')).convert('RGBA')
        # We need a text layer here for the rotation
        font, text = auto_text_size(text, ImageFont.truetype('assets/assets/fonts/sans.ttf'),
                                    125, font_scalar=0.7)
        canv = ImageDraw.Draw(base)
        render_text_with_emoji(base, canv, (525, 762), text, font, 'black')
        base = base.convert('RGB')

        b = BytesIO()
        base.save(b, format='jpeg')
        b.seek(0)
        return send_file(b, mimetype='image/jpeg')

from io import BytesIO

from PIL import Image, ImageDraw, ImageFont
from flask import send_file


from assets.utils.textutils import auto_text_size, render_text_with_emoji



class KnowYourLocation():
    params = ['text']

    def generate(self, avatars, text, usernames, kwargs):
        base = Image.open(('assets/assets/knowyourlocation/knowyourlocation.bmp')).convert('RGBA')
        # We need a text layer here for the rotation
        canv = ImageDraw.Draw(base)

        text = text.split(', ')

        if len(text) != 2:
            text = ["Separate the items with a", "comma followed by a space"]

        top, bottom = text

        top_font, top_text = auto_text_size(top, ImageFont.truetype('assets/assets/fonts/sans.ttf'), 630)
        bottom_font, bottom_text = auto_text_size(bottom,
                                                  ImageFont.truetype('assets/assets/fonts/sans.ttf'),
                                                  539)
        render_text_with_emoji(base, canv, (64, 131), top_text, top_font, 'black')
        render_text_with_emoji(base, canv, (120, 450), bottom_text, bottom_font, 'black')
        base = base.convert('RGB')

        b = BytesIO()
        base.save(b, format='jpeg')
        b.seek(0)
        return b

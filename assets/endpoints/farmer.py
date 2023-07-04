from io import BytesIO

from PIL import Image, ImageDraw, ImageFont
from flask import send_file


from assets.utils.textutils import render_text_with_emoji, wrap



class Farmer():
    params = ['text']

    def generate(self, avatars, text, usernames, kwargs):
        base = Image.open(('assets/assets/farmer/farmer.jpg'))
        font = ImageFont.truetype('assets/assets/fonts/verdana.ttf', size=24)
        canv = ImageDraw.Draw(base)

        clouds, farmer = text.replace(', ', ',').split(',', 1)

        if len(clouds) >= 150:
            clouds = clouds[:147] + '...'

        if len(farmer) >= 100:
            farmer = farmer[:97] + '...'
        render_text_with_emoji(base, canv, (50, 300), wrap(font, clouds, 580), font, 'white')
        render_text_with_emoji(base, canv, (50, 825), wrap(font, farmer, 580), font, 'white')

        base = base.convert('RGB')
        b = BytesIO()
        base.save(b, format='jpeg')
        b.seek(0)
        return b

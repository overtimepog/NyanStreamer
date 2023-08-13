
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont
from flask import send_file
from assets.utils import http


class Rate():
    params = ['avatar0']

    def generate(self, avatars, text, usernames, kwargs):
        base = Image.open(('assets/assets/rate/rate.bmp'))
        avatar = http.get_image(avatars[0]).convert('LA').resize((350, 350))
        base.paste(avatar, (285, 82), avatar)
        draw = ImageDraw.Draw(base)
        font = ImageFont.truetype('assets/fonts/MontserratBold.ttf', 30)  # Adjust font size as needed
        draw.text((333, 316), text, font=font, fill="white")
        base = base.convert('RGBA')
        b = BytesIO()
        base.save(b, format='png')
        b.seek(0)
        return b
from io import BytesIO

from PIL import Image
from flask import send_file

from assets.utils import http




class Ugly():
    params = ['avatar0']

    def generate(self, avatars, text, usernames, kwargs):
        base = Image.open(('assets/assets/ugly/ugly.bmp')).convert('RGBA')
        avatar = http.get_image(avatars[0]).resize((175, 175)).convert('RGBA')
        base.paste(avatar, (120, 55), avatar)
        base = base.convert('RGBA')

        b = BytesIO()
        base.save(b, format='png')
        b.seek(0)
        return b

from io import BytesIO

from PIL import Image
from flask import send_file

from assets.utils import http




class BongoCat():
    params = ['avatar0']

    def generate(self, avatars, text, usernames, kwargs):
        base = Image.open(('assets/bongocat/bongocat.bmp')).convert('RGBA')
        avatar = http.get_image(avatars[0]).resize((750, 750)).convert('RGBA')

        avatar.paste(base, (0, 0), base)
        avatar = avatar.convert('RGBA')

        b = BytesIO()
        avatar.save(b, format='png')
        b.seek(0)
        return send_file(b, mimetype='image/png')

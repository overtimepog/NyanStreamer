from io import BytesIO

from PIL import Image
from flask import send_file

from assets.utils import http




class Failure():
    params = ['avatar0']

    def generate(self, avatars, text, usernames, kwargs):
        base = Image.open(('assets/failure/failure.bmp')).convert('RGBA')
        avatar = http.get_image(avatars[0]).resize((215, 215)).convert('RGBA')

        base.paste(avatar, (143, 525), avatar)
        base = base.convert('RGBA')

        b = BytesIO()
        base.save(b, format='png')
        b.seek(0)
        return send_file(b, mimetype='image/png')

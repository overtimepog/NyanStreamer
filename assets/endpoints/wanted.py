from io import BytesIO

from PIL import Image
from flask import send_file

from assets.utils import http




class Wanted():
    params = ['avatar0']

    def generate(self, avatars, text, usernames, kwargs):
        base = Image.open(('assets/wanted/wanted.bmp')).convert('RGBA')
        avatar = http.get_image(avatars[0]).resize((447, 447)).convert('RGBA')
        base.paste(avatar, (145, 282), avatar)

        b = BytesIO()
        base.save(b, format='png')
        b.seek(0)
        return send_file(b, mimetype='image/png')

from io import BytesIO

from PIL import Image
from flask import send_file

from assets.utils import http




class Rip():
    params = ['avatar0']

    def generate(self, avatars, text, usernames, kwargs):
        base = Image.open(('assets/assets/rip/rip.bmp')).convert('RGBA').resize((642, 806))
        avatar = http.get_image(avatars[0]).resize((300, 300)).convert('RGBA')

        base.paste(avatar, (175, 385), avatar)
        base = base.convert('RGBA')

        b = BytesIO()
        base.save(b, format='png')
        b.seek(0)
        return send_file(b, mimetype='image/png')

from io import BytesIO

from PIL import Image
from flask import send_file

from assets.utils import http




class Roblox():
    params = ['avatar0']

    def generate(self, avatars, text, usernames, kwargs):
        base = Image.open(self.assets.get('assets/roblox/roblox.bmp')).convert('RGBA')
        avatar = http.get_image(avatars[0]).resize((56, 74)).convert('RGBA')
        base.paste(avatar, (168, 41), avatar)

        b = BytesIO()
        base.save(b, format='png')
        b.seek(0)
        return send_file(b, mimetype='image/png')

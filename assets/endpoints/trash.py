from io import BytesIO

from PIL import Image, ImageFilter
from flask import send_file

from assets.utils import http




class Trash():
    params = ['avatar0']

    def generate(self, avatars, text, usernames, kwargs):
        avatar = http.get_image(avatars[0]).resize((483, 483)).convert('RGBA')
        base = Image.open(('assets/assets/trash/trash.bmp')).convert('RGBA')

        avatar = avatar.filter(ImageFilter.GaussianBlur(radius=6))
        base.paste(avatar, (480, 0), avatar)
        base = base.convert('RGBA')

        b = BytesIO()
        base.save(b, format='png')
        b.seek(0)
        return send_file(b, mimetype='image/png')

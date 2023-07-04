from io import BytesIO

from PIL import Image
from flask import send_file

from assets.utils import http




class Whodidthis():
    params = ['avatar0']

    def generate(self, avatars, text, usernames, kwargs):
        base = Image.open(('assets/assets/whodidthis/whodidthis.bmp'))
        avatar = http.get_image(avatars[0]).resize((720, 405)).convert('RGBA')
        base.paste(avatar, (0, 159), avatar)
        base = base.convert('RGBA')

        b = BytesIO()
        base.save(b, format='png')
        b.seek(0)
        return send_file(b, mimetype='image/png')

from io import BytesIO

from PIL import Image
from flask import send_file

from assets.utils import http




class Dab():
    params = ['avatar0']

    def generate(self, avatars, text, usernames, kwargs):
        base = Image.open(('assets/assets/dab/dab.bmp')).convert('RGBA')
        avatar = http.get_image(avatars[0]).resize((500, 500)).convert('RGBA')
        final_image = Image.new('RGBA', base.size)

        # Put the base over the avatar
        final_image.paste(avatar, (300, 0), avatar)
        final_image.paste(base, (0, 0), base)

        b = BytesIO()
        final_image.save(b, format='png')
        b.seek(0)
        return send_file(b, mimetype='image/png')

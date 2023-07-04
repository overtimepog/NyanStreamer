from io import BytesIO

from flask import send_file

from assets.utils import gm




class RadialBlur():
    params = ['avatar0']

    def generate(self, avatars, text, usernames, kwargs):
        output = gm.radial_blur(avatars[0], 15, 'png')

        b = BytesIO(output)
        b.seek(0)
        return send_file(b, mimetype='image/png')

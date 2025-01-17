from io import BytesIO

from PIL import Image
from flask import send_file

from assets.utils import http

from assets.utils.skew import skew


class IPad():
    params = ['avatar0']

    def generate(self, avatars, text, usernames, kwargs):
        white = Image.new('RGBA', (2048, 1364), 0x00000000)
        base = Image.open(('assets/assets/ipad/ipad.png'))
        img1 = http.get_image(avatars[0]).convert('RGBA').resize((512, 512), Image.LANCZOS)

        img1 = skew(img1, [(476, 484), (781, 379), (956, 807), (668, 943)])
        white.paste(img1, (0, 0), img1)
        white.paste(base, (0, 0), base)
        white = white.convert('RGBA').resize((512, 341), Image.LANCZOS)

        b = BytesIO()
        white.save(b, format='png')
        b.seek(0)
        return b

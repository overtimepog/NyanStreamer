from io import BytesIO

from PIL import Image
from flask import send_file

from assets.utils import http

from assets.utils.skew import skew


class Kimborder():
    params = ['avatar0']

    def generate(self, avatars, text, usernames, kwargs):
        base = Image.open(('assets/assets/kimborder/kimborder.png'))
        white = Image.new('RGBA', (base.width, base.height), 0x00000000)
        img1 = http.get_image(avatars[0]).convert('RGBA')
        img1 = img1.resize((img1.width, img1.height), Image.LANCZOS)

        img1 = skew(img1, [(0, 402), (476, 413), (444, 638), (0, 638)])
        white.paste(img1, (0, 0), img1)
        white.paste(base, (0, 0), base)
        white = white.convert('RGBA').resize((base.width, base.height), Image.LANCZOS)

        b = BytesIO()
        white.save(b, format='png')
        b.seek(0)
        return b

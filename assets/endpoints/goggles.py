from io import BytesIO

from PIL import Image
from flask import send_file

from assets.utils import http
from assets.utils.skew import skew




class Goggles():
    params = ['avatar0']

    def generate(self, avatars, text, usernames, kwargs):
        img1 = http.get_image(avatars[0]).convert('RGBA')
        base = Image.open(('assets/assets/goggles/goggles.jpg')).convert('RGBA')
        img1 = skew(img1, [(32, 297), (171, 295), (180, 456), (41, 463)])
        base.paste(img1, (0, 0), img1)
        base = base.resize((base.width, int(base.height / 1.5)), Image.LANCZOS).convert('RGB')

        b = BytesIO()
        base.save(b, format='jpeg')
        b.seek(0)
        return b

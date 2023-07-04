from io import BytesIO

from PIL import Image
from flask import send_file

from assets.utils import http




class Aborted():
    params = ['avatar0']

    def generate(self, avatars, text, usernames, kwargs):
        base = Image.open(('assets/assets/aborted/aborted.bmp'))
        img1 = http.get_image(avatars[0]).convert('RGBA').resize((90, 90))
        base.paste(img1, (390, 130), img1)
        base = base.convert('RGB')

        b = BytesIO()
        base.save(b, format='jpeg')
        b.seek(0)
        return b

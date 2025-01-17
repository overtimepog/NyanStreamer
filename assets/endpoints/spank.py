from io import BytesIO

from PIL import Image
from flask import send_file

from assets.utils import http




class Spank():
    params = ['avatar0', 'avatar1']

    def generate(self, avatars, text, usernames, kwargs):
        base = Image.open(('assets/assets/spank/spank.bmp')).resize((500, 500))
        img1 = http.get_image(avatars[0]).resize((140, 140)).convert('RGBA')
        img2 = http.get_image(avatars[1]).resize((120, 120)).convert('RGBA')
        base.paste(img1, (225, 5), img1)
        base.paste(img2, (350, 220), img2)
        base = base.convert('RGBA')

        b = BytesIO()
        base.save(b, format='png')
        b.seek(0)
        return b

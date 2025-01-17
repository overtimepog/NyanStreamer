from io import BytesIO

from PIL import Image
from flask import send_file

from assets.utils import http




class Jail():
    params = ['avatar0']

    def generate(self, avatars, text, usernames, kwargs):
        overlay = Image.open(('assets/assets/jail/jail.bmp')).resize((350, 350))
        base = http.get_image(avatars[0]).convert('LA').resize((350, 350))
        base.paste(overlay, (0, 0), overlay)

        base = base.convert('RGBA')
        b = BytesIO()
        base.save(b, format='png')
        b.seek(0)
        return b

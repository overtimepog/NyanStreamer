from io import BytesIO

from PIL import Image
from flask import send_file

from assets.utils import http




class Slap():
    params = ['avatar0', 'avatar1']

    def generate(self, avatars, text, usernames, kwargs):
        base = Image.open(('assets/assets/batslap/batslap.bmp')).resize((1000, 500)).convert('RGBA')
        avatar = http.get_image(avatars[1]).resize((220, 220)).convert('RGBA')
        avatar2 = http.get_image(avatars[0]).resize((200, 200)).convert('RGBA')
        base.paste(avatar, (580, 260), avatar)
        base.paste(avatar2, (350, 70), avatar2)
        base = base.convert('RGB')

        b = BytesIO()
        base.save(b, format='png')
        b.seek(0)
        return b

from io import BytesIO
from random import randint

from PIL import Image, ImageEnhance
from flask import send_file

from assets.utils import http, noisegen




class DeepFry():
    params = ['avatar0']

    def generate(self, avatars, text, usernames, kwargs):
        avatar = http.get_image(avatars[0]).resize((400, 400)).convert('RGBA')

        # noinspection PyPep8
        joy, hand, hundred, fire = [
            Image.open((f'assets/assets/deepfry/{asset}.bmp'))
            .resize((100, 100))
            .rotate(randint(-30, 30))
            .convert('RGBA')
            for asset in ['joy', 'ok-hand', '100', 'fire']
        ]

        avatar.paste(joy, (randint(20, 75), randint(20, 45)), joy)
        avatar.paste(hand, (randint(20, 75), randint(150, 300)), hand)
        avatar.paste(hundred, (randint(150, 300), randint(20, 45)), hundred)
        avatar.paste(fire, (randint(150, 300), randint(150, 300)), fire)

        noise = avatar.convert('RGB')
        noise = noisegen.add_noise(noise, 25)
        noise = ImageEnhance.Contrast(noise).enhance(randint(5, 20))
        noise = ImageEnhance.Sharpness(noise).enhance(17.5)
        noise = ImageEnhance.Color(noise).enhance(randint(-15, 15))

        b = BytesIO()
        noise.save(b, format='png')
        b.seek(0)
        return b

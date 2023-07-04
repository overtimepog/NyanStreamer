from io import BytesIO

from PIL import Image, ImageDraw, ImageFont
from flask import send_file


from assets.utils.textutils import render_text_with_emoji, wrap



class Inator():
    params = ['text']

    def generate(self, avatars, text, usernames, kwargs):
        base = Image.open(('assets/assets/inator/inator.jpg'))
        font = ImageFont.truetype('assets/assets/fonts/verdana.ttf', size=24)
        canv = ImageDraw.Draw(base)
        render_text_with_emoji(base, canv, (370, 0), wrap(font, text, 340), font, 'black')
        vowels = ['i', 'y', 'e', 'a', 'u', 'o']
        for vowel in vowels:
            if text.endswith(vowel):
                ending = 'nator'
                break
        else:
            ending = 'inator'
        render_text_with_emoji(base, canv, (370, 380), wrap(font, text + ending, 335), font, 'black')
        base = base.convert('RGB')
        b = BytesIO()
        base.save(b, format='jpeg')
        b.seek(0)
        return send_file(b, mimetype='image/jpeg')

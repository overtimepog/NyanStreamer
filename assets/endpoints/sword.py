from io import BytesIO

from PIL import Image, ImageDraw, ImageFont
from flask import send_file


from assets.utils.textutils import wrap, render_text_with_emoji



class Sword():
    params = ['text', 'username0']

    def generate(self, avatars, text, usernames, kwargs):
        text = text.replace(', ', ',').split(',')
        if len(text) != 2:
            text = ['SPLIT BY', 'COMMA']
        base = Image.open(('assets/assets/sword/sword.bmp'))
        font = ImageFont.truetype('assets/assets/fonts/verdana.ttf', size=48)
        temp = Image.new('RGBA', (1200, 800), color=(0, 0, 0, 0))

        sword = wrap(font, text[0], 3000)
        food = wrap(font, text[1], 300)
        canv = ImageDraw.Draw(base)
        temp_draw = ImageDraw.Draw(temp)
        render_text_with_emoji(temp, temp_draw, (0, 0), sword, font=font, fill='White')
        temp = temp.rotate(-25, expand=1)
        render_text_with_emoji(base, canv, (330, 330), usernames[0], font=font, fill='White')

        base.paste(temp, (-30, 605), temp)

        size = canv.textsize(food, font=font)

        new_width = (base.width - size[0]) / 2

        render_text_with_emoji(base, canv, (new_width - 20, 830), food, font=font, fill='Black')

        base = base.convert('RGB')
        b = BytesIO()
        base.save(b, format='jpeg')
        b.seek(0)
        return send_file(b, mimetype='image/jpeg')

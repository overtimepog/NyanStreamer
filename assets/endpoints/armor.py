from io import BytesIO

from PIL import Image, ImageDraw
from flask import send_file


from assets.utils.textutils import auto_text_size, render_text_with_emoji



class Armor():
    params = ['text']

    def generate(self, avatars, text, usernames, kwargs):
        base = Image.open(self.assets.get('assets/armor/armor.bmp')).convert('RGBA')
        # We need a text layer here for the rotation
        font, text = auto_text_size(text, self.assets.get_font('assets/fonts/sans.ttf'), 207,
                                    font_scalar=0.8)
        canv = ImageDraw.Draw(base)

        render_text_with_emoji(base, canv, (34, 371), text, font=font, fill='Black')
        base = base.convert('RGB')

        b = BytesIO()
        base.save(b, format='jpeg')
        b.seek(0)
        return send_file(b, mimetype='image/jpeg')

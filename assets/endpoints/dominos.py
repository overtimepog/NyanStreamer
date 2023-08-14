from PIL import Image, ImageDraw, ImageFont
from assets.utils import http
from io import BytesIO

class Dominoes:
    """
    This endpoint returns an image with text1 and text2 placed at specific coordinates.
    Ensure your application can handle the image format.
    Malformed requests count against your ratelimit for this endpoint.
    Place text1 and text2 on the image at the specified coordinates.
    """
    params = ['text1', 'text2']

    def generate(self, avatars, text, usernames, kwargs):
        # Load the main image from the specified path
        main_img = Image.open('assets/assets/dominos/dominos.png')
        
        # Create a drawing context
        draw = ImageDraw.Draw(main_img)
        
        # Extract text1 and text2 from the text parameter
        text1, text2 = text.split(',')
        
        # Define the font for the text using the provided path and adjust its size to fit the area
        font_size = 30
        font = ImageFont.truetype('assets/assets/fonts/Arial-Bold.ttf', font_size)
        while draw.textsize(text1, font=font)[0] > (771 - 612) and font_size > 10:
            font_size -= 1
            font = ImageFont.truetype('assets/assets/fonts/Arial-Bold.ttf', font_size)
        
        # Place text1 at the specified coordinates
        draw.text((612, 357), text1, font=font, fill="white")
        
        # Adjust font size for text2
        font_size = 30
        font = ImageFont.truetype('assets/assets/fonts/Arial-Bold.ttf', font_size)
        while draw.textsize(text2, font=font)[0] > (162 - 30) and font_size > 10:
            font_size -= 1
            font = ImageFont.truetype('assets/assets/fonts/Arial-Bold.ttf', font_size)
        
        # Place text2 at the specified coordinates
        draw.text((30, 41), text2, font=font, fill="white")
        
        # Convert the image to bytes and return
        b = BytesIO()
        main_img.save(b, format='PNG')
        b.seek(0)
        return b
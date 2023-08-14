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
        
        # Define the font for the text using the provided path
        font = ImageFont.truetype('assets/assets/fonts/Arial-Bold.ttf', 30)  # Adjust font size as needed
        
        # Extract text1 and text2 from the text parameter
        text1, text2 = text.split(',')
        
        # Place text1 and text2 at the specified coordinates
        draw.text((612, 357), text1, font=font, fill="white")
        draw.text((30, 41), text2, font=font, fill="white")
        
        # Convert the image to bytes and return
        b = BytesIO()
        main_img.save(b, format='PNG')
        b.seek(0)
        return b
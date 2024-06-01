from PIL import Image, ImageDraw, ImageFont
from assets.utils import http
from io import BytesIO

class JohnOliver:
    """
    This endpoint returns an image with the user's avatar placed at specific coordinates.
    Ensure your application can handle the image format.
    Malformed requests count against your ratelimit for this endpoint.
    Place the user's avatar on an image at the coordinates 54,50,378,293 and add text to the bottom middle.
    """
    params = ['avatar0', 'text']

    def generate(self, avatars, text, usernames, kwargs):
        # Load the main image from the specified path
        main_img = Image.open('assets/assets/johnoliver/johnoliver.png')
        
        # Fetch the user's avatar using http.get_image and convert it to a PIL Image
        avatar_img = http.get_image(avatars[0]).convert('RGBA')
        
        # Resize the avatar to fit the specified coordinates
        avatar_img = avatar_img.resize((378 - 54, 293 - 50))
        
        # Paste the avatar onto the main image
        main_img.paste(avatar_img, (54, 50), avatar_img if avatar_img.mode == 'RGBA' else None)
        
        # Add text to the bottom middle of the image
        draw = ImageDraw.Draw(main_img)
        font = ImageFont.truetype('assets/assets/fonts/Arial-Bold.ttf', 30)  # Adjust font size and path as needed
        
        # Get the bounding box of the text
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Calculate the text position
        text_position = ((main_img.width - text_width) // 2, main_img.height - text_height - 20)
        
        # Draw the text on the image
        draw.text(text_position, text, font=font, fill="white")
        
        # Convert the image to bytes and return
        b = BytesIO()
        main_img.save(b, format='PNG')
        b.seek(0)
        return b
from PIL import Image
from assets.utils import http
from io import BytesIO

class JohnOliver:
    """
    This endpoint returns an image with the user's avatar placed at specific coordinates.
    Ensure your application can handle the image format.
    Malformed requests count against your ratelimit for this endpoint.
    Place the user's avatar on an image at the coordinates 54,50,378,293.
    """
    params = ['avatar0']

    def generate(self, avatars, text, usernames, kwargs):
        # Load the main image from the specified path
        main_img = Image.open('assets/assets/johnoliver/johnoliver.png')
        
        # Fetch the user's avatar using http.get_image and convert it to a PIL Image
        avatar_img = Image.open(http.get_image(avatars[0]))
        
        # Resize the avatar to fit the specified coordinates
        avatar_img = avatar_img.resize((378 - 54, 293 - 50))
        
        # Paste the avatar onto the main image
        main_img.paste(avatar_img, (54, 50), avatar_img if avatar_img.mode == 'RGBA' else None)
        
        # Convert the image to bytes and return
        b = BytesIO()
        main_img.save(b, format='PNG')
        b.seek(0)
        return b

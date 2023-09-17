from io import BytesIO
from PIL import Image

class Suffering():
    params = ['avatar0']

    def generate(self, avatars, text, usernames, kwargs):
        # Open the main image
        base = Image.open('assets/assets/suffering/suffering.png').convert('RGBA')
        
        # Get the avatar image and resize it to fit the coordinates
        response = requests.get(avatars[0])
        avatar_data = BytesIO(response.content)
        avatar = Image.open(avatar_data).resize((1227-650, 849-265)).convert('RGBA')
        
        # Paste the avatar image onto the main image at the specified coordinates
        base.paste(avatar, (650, 265), avatar)
        
        # Convert the resulting image to RGBA format
        base = base.convert('RGBA')

        # Save the resulting image to a BytesIO object
        b = BytesIO()
        base.save(b, format='png')
        b.seek(0)
        return b

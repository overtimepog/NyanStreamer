from PIL import Image, ImageDraw, ImageFont, ImageSequence
from io import BytesIO

class BeeMovieLawyer:
    """
    This endpoint returns a GIF with text placed at specific coordinates.
    Ensure your application can handle the GIF format.
    Malformed requests count against your ratelimit for this endpoint.
    Dynamically place the text on the GIF within the coordinates starting at -1,2 and ending at 719,240.
    """
    params = ['text']

    def generate(self, avatars, text, usernames, kwargs):
        # Load the GIF from the specified path
        gif = Image.open('assets/assets/beemovielawyer/beemovielawyer.gif')
        
        # Define the font for the text using the provided path
        font_size = 30
        font = ImageFont.truetype('assets/assets/fonts/Arial-Bold.ttf', font_size)
        
        # Calculate text width and height
        text_width, text_height = ImageDraw.Draw(gif).multiline_textsize(text, font=font)
        
        # Adjust font size if text width is greater than the specified width
        while text_width > 720:
            font_size -= 1
            font = ImageFont.truetype('assets/assets/fonts/Arial-Bold.ttf', font_size)
            text_width, text_height = ImageDraw.Draw(gif).multiline_textsize(text, font=font)
        
        # Calculate position to center the text
        x_pos = (-1 + 719 - text_width) // 2
        y_pos = (2 + 240 - text_height) // 2
        
        frames = []
        for frame in ImageSequence.Iterator(gif):
            # Create a drawing context
            draw = ImageDraw.Draw(frame)
            
            # Place the text at the calculated coordinates
            draw.text((x_pos, y_pos), text, font=font, fill="white")
            
            # Append the frame to the frames list
            frames.append(frame.copy())
        
        # Convert the frames to GIF and return
        b = BytesIO()
        frames[0].save(b, format='GIF', append_images=frames[1:], save_all=True, duration=gif.info['duration'], loop=0)
        b.seek(0)
        return b

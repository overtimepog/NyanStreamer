from PIL import Image, ImageDraw, ImageFont, ImageSequence
from assets.utils import http
from io import BytesIO

class BeeMovieLawyer:
    """
    This endpoint returns a GIF with text placed at specific coordinates.
    Ensure your application can handle the GIF format.
    Malformed requests count against your ratelimit for this endpoint.
    Place text on the GIF at the specified coordinates.
    """
    params = ['text']

    def generate(self, avatars, text, usernames, kwargs):
        # Load the GIF
        gif = Image.open('assets/assets/beemovielawyer/beemovielawyer.gif')
        
        # Create a drawing context
        frames = []
        font_path = 'assets/assets/fonts/impact.ttf'
        max_width = 639
        max_height = 208
        initial_font_size = 40
        font = ImageFont.truetype(font_path, initial_font_size)

        # Reduce font size until the text width is less than max_width
        while font.getsize(text)[0] > max_width:
            initial_font_size -= 1
            font = ImageFont.truetype(font_path, initial_font_size)

        # Wrap text if it's too long to fit on one line
        wrapped_text = ""
        for word in text.split():
            if font.getsize(wrapped_text + word)[0] <= max_width:
                wrapped_text += word + " "
            else:
                wrapped_text += "\n" + word + " "
        
        # Split the wrapped text into lines
        lines = wrapped_text.split("\n")
        
        # Ensure the total height of the text block doesn't exceed max_height
        while len(lines) * font.getsize(lines[0])[1] > max_height:
            initial_font_size -= 1
            font = ImageFont.truetype(font_path, initial_font_size)
            wrapped_text = ""
            for word in text.split():
                if font.getsize(wrapped_text + word)[0] <= max_width:
                    wrapped_text += word + " "
                else:
                    wrapped_text += "\n" + word + " "
            lines = wrapped_text.split("\n")

        # Calculate the starting y-coordinate to center the text vertically
        y_start = (max_height - len(lines) * font.getsize(lines[0])[1]) // 2

        for frame in ImageSequence.Iterator(gif):
            d = ImageDraw.Draw(frame)
            y = y_start
            for line in lines:
                width, height = d.textsize(line, font=font)
                # Draw text centered in the specified rectangle
                d.text(((max_width - width) / 2, y), line, font=font, fill="white")
                y += height
            frames.append(frame)

        # Convert the frames to bytes and return
        b = BytesIO()
        frames[0].save(b, format='GIF', append_images=frames[1:], save_all=True, duration=gif.info['duration'], loop=0)
        b.seek(0)
        return b
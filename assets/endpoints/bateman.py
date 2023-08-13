from assets.utils import http
from moviepy.editor import VideoFileClip
from PIL import Image
import uuid
import os
from io import BytesIO
import numpy as np

class Bateman:
    """
    This endpoint returns an MP4 file. Ensure your application can handle this format.
    Malformed requests count against your ratelimit for this endpoint.
    Replace the green screen in the video with a user's avatar.
    """
    params = ['avatar0']

    def generate(self, avatars, text, usernames, kwargs):
        name = uuid.uuid4().hex + '.mp4'

        # Load the video from the provided path
        video = VideoFileClip('assets/assets/patrickBateman/PatrickBateman.mp4')
        
        # Fetch the avatar using http.get_image and convert it to a PIL Image
        avatar_img = http.get_image(avatars[0]).convert('RGB').resize(video.size)
        avatar_np = np.array(avatar_img)  # Convert PIL Image to numpy array
        
        def replace_green_screen(frame):
            output_frame = frame.copy()

            # Create a mask where green is dominant
            green_mask = (frame[:,:,1] > 100) & (frame[:,:,0] < 75) & (frame[:,:,2] < 75)

            # Replace green screen pixels with avatar pixels
            output_frame[green_mask] = avatar_np[green_mask]
            
            return output_frame

        # Apply the replacement function to each frame of the video
        final_video = video.fl_image(replace_green_screen)

        # Write the video to a temporary file
        final_video.write_videofile(name, threads=4, preset='superfast', verbose=False)

        # Read the video data from the file
        with open(name, 'rb') as f:
            video_data = BytesIO(f.read())

        # Remove the temporary file
        os.remove(name)

        return video_data
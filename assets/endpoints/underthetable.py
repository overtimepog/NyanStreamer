from assets.utils import http
from moviepy.editor import VideoFileClip
from PIL import Image
import numpy as np
import uuid
import os
from io import BytesIO

class UnderTheTable:
    """
    This endpoint returns an MP4 file. Ensure your application can handle this format.
    Malformed requests count against your ratelimit for this endpoint.
    Replace the green screen in the video with a user's avatar.
    """
    params = ['avatar0']

    def generate(self, avatars, text, usernames, kwargs):
        name = uuid.uuid4().hex + '.mp4'

        # Load the video from the provided path
        video = VideoFileClip('assets/assets/underthetable/underthetable.mp4')
        
        # Fetch the avatar using http.get_image and convert it to a PIL Image
        avatar_img = http.get_image(avatars[0]).convert('RGB').resize(video.size)
        avatar_np = np.array(avatar_img)  # Convert PIL Image to numpy array
        
        def replace_green_screen(frame):
            output_frame = frame.copy()  # Create a writable copy
            for x in range(output_frame.shape[1]):
                for y in range(output_frame.shape[0]):
                    red, green, blue = output_frame[y, x]
                    if green > 100 and red < 75 and blue < 75:
                        output_frame[y, x] = avatar_np[y, x]  # Now, avatar_np is also a 3D array
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
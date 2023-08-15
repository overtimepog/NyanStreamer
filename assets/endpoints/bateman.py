from assets.utils import http
from moviepy.editor import VideoFileClip, ImageSequenceClip
from PIL import Image
import uuid
import os
from io import BytesIO
import numpy as np
import concurrent.futures

class Bateman:
    """
    This endpoint returns an MP4 file. Ensure your application can handle this format.
    Malformed requests count against your ratelimit for this endpoint.
    Replace the green screen in the video with a user's avatar.
    """
    params = ['avatar0']

    def replace_green_screen(self, frame, avatar_np):
        output_frame = frame.copy()
        green_mask = (frame[:,:,1] > 100) & (frame[:,:,0] < 75) & (frame[:,:,2] < 75)
        output_frame[green_mask] = avatar_np[green_mask]
        return output_frame

    def generate(self, avatars, text, usernames, kwargs):
        name = uuid.uuid4().hex + '.mp4'

        # Load the video from the provided path
        video = VideoFileClip('assets/assets/patrickBateman/PatrickBateman.mp4')
        
        # Fetch the avatar using http.get_image and convert it to a PIL Image
        avatar_img = http.get_image(avatars[0]).convert('RGB').resize(video.size)
        avatar_np = np.array(avatar_img)  # Convert PIL Image to numpy array

        # Process frames concurrently
        with concurrent.futures.ThreadPoolExecutor() as executor:
            frames = list(executor.map(lambda frame: self.replace_green_screen(np.array(frame), avatar_np), video.iter_frames()))

        # Convert frames back to video
        final_video = ImageSequenceClip(frames, fps=video.fps)

        # Write the video to a temporary file
        final_video.write_videofile(name, threads=4, preset='superfast', verbose=False)

        # Read the video data from the file
        with open(name, 'rb') as f:
            video_data = BytesIO(f.read())

        # Remove the temporary file
        os.remove(name)

        return video_data
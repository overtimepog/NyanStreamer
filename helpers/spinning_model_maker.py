from panda3d.core import Point3, Vec3, PNMImage, Texture, FrameBufferProperties, GraphicsPipe, WindowProperties
from direct.showbase.ShowBase import ShowBase
import os
from PIL import Image, ImageSequence
import requests
from io import BytesIO
import sys
import subprocess
from panda3d.core import loadPrcFileData
import fcntl
import hashlib
import time

class ModelViewer(ShowBase):
    def __init__(self, model_path, image_url, save_path, frames, filename,
                 model_pos=(0, 0, 0), model_hpr=(0, 96, 25), 
                 cam_pos=(0, -3, 0)):

        loadPrcFileData("", "window-type offscreen")
        loadPrcFileData("", "audio-library-name null")
        ShowBase.__init__(self)

        self.model_path = model_path
        self.frames = []
        self.frame_counter = 0
        self.total_frames = frames
        self.rotation_speed = 360.0 / self.total_frames
        self.filename = filename

        # Ensure the frames directory exists
        frames_dir = "assets/frames"
        os.makedirs(frames_dir, exist_ok=True)

        if self.model_path.endswith('.obj'):
            print("Converting .obj to .egg...")
            egg_path = self.model_path.replace('.obj', '.egg')
            subprocess.run(['obj2egg', '-o', egg_path, self.model_path])
            if not os.path.exists(egg_path):
                print("Failed to convert .obj to .egg.")
                return
            self.model_path = egg_path
            print(".obj converted to .egg successfully!")
            
        print("Loading the 3D model...")
        self.model = self.loader.loadModel(self.model_path)
        if not self.model:
            print("Failed to load the model.")
            return
        print("Model loaded successfully!")

        min_point, max_point = self.model.getTightBounds()
        max_dim = max_point - min_point
        scale_factor = 1.8 / max_dim.length()
        self.model.setScale(scale_factor)

        response = requests.get(image_url)
        response.raise_for_status()

        image = Image.open(BytesIO(response.content))
        if image.is_animated:
            image = ImageSequence.Iterator(image)[0]

        if image.mode == 'RGBA':
            background = Image.new('RGB', image.size, (255, 255, 255))
            background.paste(image, mask=image.split()[3])
            image = background

        image = image.resize((1920, 1080))
        image.save(save_path, "PNG")

        self.texture = self.loader.loadTexture(save_path)
        self.model.setTexture(self.texture, 1)

        self.model.setPos(*model_pos)
        self.model.setHpr(*model_hpr)
        self.model.reparentTo(self.render)

        self.cam.setPos(*cam_pos)

        self.setup_lighting()
        self.setup_offscreen_buffer()
        self.taskMgr.add(self.spin_task, "spin_task")

    def setup_lighting(self):
        from panda3d.core import AmbientLight, DirectionalLight

        ambient = AmbientLight("ambient_light")
        ambient.setColor((0.2, 0.2, 0.2, 1))
        ambient_np = self.render.attachNewNode(ambient)
        self.render.setLight(ambient_np)

        directional = DirectionalLight("directional_light")
        directional.setDirection(Vec3(0, 8, -2.5))
        directional.setColor((1, 1, 1, 1))
        directional_np = self.render.attachNewNode(directional)
        self.render.setLight(directional_np)

    def setup_offscreen_buffer(self):
        fb_props = FrameBufferProperties()
        fb_props.setRgbaBits(8, 8, 8, 8)
        fb_props.setDepthBits(1)
        win_props = WindowProperties.size(self.win.getXSize(), self.win.getYSize())
        self.buffer = self.graphicsEngine.makeOutput(self.pipe, "offscreen buffer", -2, fb_props, win_props,
                                                     GraphicsPipe.BFRefuseWindow, self.win.getGsg(), self.win)
        self.buffer.setClearColor((1, 1, 1, 1))

        dr = self.buffer.makeDisplayRegion()
        dr.setCamera(self.cam)
        
    def remove_background(self, input_path, output_path):
        """Remove background using ImageMagick."""
        if not os.path.exists(input_path):
            print(f"Error: {input_path} does not exist.")
            return
        cmd = [
            'convert', input_path, 
            '-fuzz', '10%',  
            '-transparent', 'white',  
            output_path
        ]
        subprocess.run(cmd)

    def spin_task(self, task):
        self.model.setH(self.model.getH() + self.rotation_speed)
        if self.frame_counter < self.total_frames:
            frame_path = os.path.join("assets/frames", f"frame_{self.frame_counter}.png")
            img = PNMImage()
            self.buffer.getScreenshot(img)
            img.write(frame_path)

            no_bg_path = os.path.join("assets/frames", f"frame_no_bg_{self.frame_counter}.png")
            self.remove_background(frame_path, no_bg_path)

            if os.path.exists(no_bg_path):
                self.frames.append(no_bg_path)
            else:
                print(f"Error: {no_bg_path} does not exist.")

            self.frame_counter += 1
            print(f"Frame {self.frame_counter} captured.")
            return task.cont
        else:
            frames = [Image.open(frame_path) for frame_path in self.frames if os.path.exists(frame_path)]
            if not frames:
                print("Error: No frames captured.")
                return task.done
            reference_frame_count = 36
            reference_duration_per_frame = 50
            actual_frame_count = len(frames)
            desired_duration_per_frame = (reference_frame_count * reference_duration_per_frame) // actual_frame_count
            with open(f'{self.filename}.gif', 'wb') as f:
                fcntl.flock(f, fcntl.LOCK_EX)
                frames[0].save(f, save_all=True, append_images=frames[1:], duration=desired_duration_per_frame, loop=0, disposal=2)
                fcntl.flock(f, fcntl.LOCK_UN)
            print(f"GIF created: {self.filename}.gif")

def spinning_chair(model_path: str, image_url: str, frames: int, filename: str, 
                   model_pos: tuple = (0, 0, 0), 
                   model_hpr: tuple = (0, 0, 0), 
                   cam_pos: tuple = (0, -3, 0)):
    
    hash_object = hashlib.md5(image_url.encode())
    hex_dig = hash_object.hexdigest()
    timestamp = int(time.time())
    save_path = f"download_{hex_dig}_{timestamp}.png"
    app = ModelViewer(model_path, image_url, save_path, frames, filename, model_pos, model_hpr, cam_pos)
    app.run()
    
    if os.path.exists(save_path):
        os.remove(save_path)

if __name__ == "__main__":
    model_path = sys.argv[1]
    image_url = sys.argv[2]
    frames = int(sys.argv[3])
    filename = sys.argv[4]
    model_pos = tuple(map(float, sys.argv[5].split(',')))
    model_hpr = tuple(map(float, sys.argv[6].split(',')))
    cam_pos = tuple(map(float, sys.argv[7].split(',')))

    spinning_chair(model_path, image_url, frames, filename, model_pos, model_hpr, cam_pos)
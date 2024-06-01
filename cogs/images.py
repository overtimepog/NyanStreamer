import io
import os
import sys
import time
import subprocess
import fcntl
import logging
import glob
import importlib
from pathlib import Path
import discord
from discord.ext import commands
from discord.ext.commands import Context
from discord import File
from typing import Any
from fastapi import BackgroundTasks, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from starlette.responses import StreamingResponse

class Images(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.endpoints = self.load_endpoints()

    def load_endpoints(self):
        endpoints = {}
        endpoints_path = Path('assets/endpoints')
        for file in endpoints_path.glob('*.py'):
            module_name = file.stem
            if module_name != '__init__':
                module = importlib.import_module(f'assets.endpoints.{module_name}')
                endpoints[module_name] = module
        return endpoints

    def wait_for_unlock(self, filename):
        timeout = 300  
        check_interval = 1  
        elapsed_time = 0

        while elapsed_time < timeout:
            try:
                with open(filename, 'rb') as f:
                    fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)  # Try to acquire an exclusive lock
                    fcntl.flock(f, fcntl.LOCK_UN)  # Release the lock
                    return
            except IOError:
                pass
            
            time.sleep(check_interval)
            elapsed_time += check_interval

        logging.error(f"Timeout reached. Failed to generate GIF: {filename}")
        raise Exception("Failed to generate GIF due to timeout")

    def delete_file(self, filename: str):
        """Delete a file after a delay to ensure it's been sent to the user."""
        time.sleep(10)  # Wait for 10 seconds to ensure the file has been sent
        if os.path.exists(filename):
            os.remove(filename)

    def delete_all_download_files(self):
        """Delete all files in the current directory that start with 'download_'."""
        for file in glob.glob("download_*"):
            try:
                os.remove(file)
                logging.info(f"Deleted file: {file}")
            except Exception as e:
                logging.error(f"Error deleting file {file}: {e}")

    def run_model_subprocess(self, model_path, avatar_url, frames, filename, angles):
        logging.info(f"Starting subprocess to generate GIF for avatar: {avatar_url}")
        
        # Use subprocess.Popen to start the process
        subprocess.Popen([sys.executable, 'helpers/spinning_model_maker.py', model_path, avatar_url, str(frames), filename, *angles])

    @commands.hybrid_command(
        name="becomeacan",
        description="generate a can GIF from an avatar",
    )
    async def become_a_can(self, ctx: Context, user: discord.User):
        avatar_url = str(user.avatar.url)
        logging.info(f"Received request to generate can GIF for avatar: {avatar_url}")
        
        frames = 24
        timestamp = int(time.time())
        filename = f"can_image_{timestamp}"  # Unique filename based on timestamp
        model_path = "/root/NyanStreamer/assets/models/Can.egg"
        
        if not os.path.exists(model_path):
            logging.error("The can model is missing.")
            await ctx.send("The can model is missing. Please try again later.")
            return
        
        # Run the image generation synchronously
        try:
            self.run_model_subprocess(model_path, avatar_url, frames, filename, ['0,0,-0.85', '0,100,0', '0,-5,0'])
            
            # Wait for the GIF to be unlocked (i.e., fully generated)
            gif_path = filename + ".gif"
            self.wait_for_unlock(gif_path)
            
            logging.info(f"Successfully generated GIF: {gif_path}")
            await ctx.send(file=discord.File(gif_path))
            
            # Schedule the cleanup task to run in the background after sending the response
            self.bot.loop.run_in_executor(None, self.delete_file, gif_path)
            self.bot.loop.run_in_executor(None, self.delete_all_download_files)
        except Exception as e:
            logging.error(f"Failed to generate GIF: {str(e)}")
            await ctx.send("Failed to generate the can GIF. Please try again.")

    @commands.hybrid_command(
        name="becomeachair",
        description="generate a chair GIF from an avatar",
    )
    async def become_a_chair(self, ctx: Context, user: discord.User):
        avatar_url = str(user.avatar.url)
        logging.info(f"Received request to generate chair GIF for avatar: {avatar_url}")
        
        frames = 24
        timestamp = int(time.time())
        filename = f"chair_image_{timestamp}"  # Unique filename based on timestamp
        model_path = "/root/NyanStreamer/assets/models/Chair.egg"
        
        if not os.path.exists(model_path):
            logging.error("The chair model is missing.")
            await ctx.send("The chair model is missing. Please try again later.")
            return
        
        # Run the image generation synchronously
        try:
            self.run_model_subprocess(model_path, avatar_url, frames, filename, ['0,0,0', '0,96,25', '0,-3,0'])
            
            # Wait for the GIF to be unlocked (i.e., fully generated)
            gif_path = filename + ".gif"
            self.wait_for_unlock(gif_path)
            
            logging.info(f"Successfully generated GIF: {gif_path}")
            await ctx.send(file=discord.File(gif_path))
            
            # Schedule the cleanup task to run in the background after sending the response
            self.bot.loop.run_in_executor(None, self.delete_file, gif_path)
            self.bot.loop.run_in_executor(None, self.delete_all_download_files)
        except Exception as e:
            logging.error(f"Failed to generate GIF: {str(e)}")
            await ctx.send("Failed to generate the chair GIF. Please try again.")

    @commands.hybrid_command(
        name="becomeanuke",
        description="generate a nuke GIF from an avatar",
    )
    async def become_a_nuke(self, ctx: Context, user: discord.User):
        avatar_url = str(user.avatar.url)
        logging.info(f"Received request to generate nuke GIF for avatar: {avatar_url}")
        
        frames = 24
        timestamp = int(time.time())
        filename = f"nuke_image_{timestamp}"  # Unique filename based on timestamp
        model_path = "/root/NyanStreamer/assets/models/Nuke.egg"
        
        if not os.path.exists(model_path):
            logging.error("The nuke model is missing.")
            await ctx.send("The nuke model is missing. Please try again later.")
            return
        
        # Run the image generation synchronously
        try:
            self.run_model_subprocess(model_path, avatar_url, frames, filename, ['0,0,0', '0,0,45', '0,-4,0'])
            
            # Wait for the GIF to be unlocked (i.e., fully generated)
            gif_path = filename + ".gif"
            self.wait_for_unlock(gif_path)
            
            logging.info(f"Successfully generated GIF: {gif_path}")
            await ctx.send(file=discord.File(gif_path))
            
            # Schedule the cleanup task to run in the background after sending the response
            self.bot.loop.run_in_executor(None, self.delete_file, gif_path)
            self.bot.loop.run_in_executor(None, self.delete_all_download_files)
        except Exception as e:
            logging.error(f"Failed to generate GIF: {str(e)}")
            await ctx.send("Failed to generate the nuke GIF. Please try again.")
            
            
    @commands.hybrid_command(
        name="johnoliver",
        description='"this is a __" with a users avatar',
    )
    async def john_oliver(self, ctx: Context, user: discord.User, *, text: str):
        avatar_url = str(user.avatar.url)
        logging.info(f"Received request to generate John Oliver image for avatar: {avatar_url}")
        
        try:
            johnoliver_instance = self.endpoints.get("johnoliver").JohnOliver()
            if not johnoliver_instance:
                raise Exception("John Oliver endpoint is missing.")
            
            image_data = johnoliver_instance.generate([avatar_url], text, [], {})
            await ctx.send(file=discord.File(fp=image_data, filename="johnoliver.png"))
        except Exception as e:
            logging.error(f"Failed to generate John Oliver image: {str(e)}")
            await ctx.send("Failed to generate the John Oliver image. Please try again.")

async def setup(bot):
    await bot.add_cog(Images(bot))
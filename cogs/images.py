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
from petpetgif import petpet
from io import BytesIO
import aiohttp

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

    async def generate_gif(self, ctx, user, model_path, position, rotation, camera):
        avatar_url = str(user.avatar.url)
        logging.info(f"Received request to generate GIF for avatar: {avatar_url}")

        frames = 24
        timestamp = int(time.time())
        filename = f"{model_path.split('/')[-1].split('.')[0]}_image_{timestamp}"  # Unique filename based on timestamp

        if not os.path.exists(model_path):
            logging.error(f"The {model_path} model is missing.")
            await ctx.send(f"The {model_path} model is missing. Please try again later.")
            return

        embed = discord.Embed(
            title="GIF Generation in Progress",
            description=f"This is where your {model_path.split('/')[-1].split('.')[0]} will go.",
            color=discord.Color.blue()
        )
        message = await ctx.send(embed=embed)

        # Run the image generation synchronously
        try:
            self.run_model_subprocess(model_path, avatar_url, frames, filename, [position, rotation, camera])
            
            # Wait for the GIF to be unlocked (i.e., fully generated)
            gif_path = filename + ".gif"
            self.wait_for_unlock(gif_path)

            logging.info(f"Successfully generated GIF: {gif_path}")
            
            file = discord.File(gif_path)
            embed = discord.Embed(
                title="GIF Generated",
                description="Here is your GIF!",
                color=discord.Color.green()
            )
            embed.set_image(url=f"attachment://{gif_path}")
            await message.edit(embed=embed)
            await ctx.send(file=file)

            # Schedule the cleanup task to run in the background after sending the response
            self.bot.loop.run_in_executor(None, self.delete_file, gif_path)
            self.bot.loop.run_in_executor(None, self.delete_all_download_files)
        except Exception as e:
            logging.error(f"Failed to generate GIF: {str(e)}")
            await ctx.send("Failed to generate the GIF. Please try again.")

    @commands.hybrid_command(
        name="becomeacan",
        description="Generate a can GIF from an avatar",
    )
    async def become_a_can(self, ctx: commands.Context, user: discord.User):
        await self.generate_gif(ctx, user, "/root/NyanStreamer/assets/models/Can.egg", '0,0,-0.85', '0,100,0', '0,-5,0')

    @commands.hybrid_command(
        name="becomeachair",
        description="Generate a chair GIF from an avatar",
    )
    async def become_a_chair(self, ctx: commands.Context, user: discord.User):
        await self.generate_gif(ctx, user, "/root/NyanStreamer/assets/models/Chair.egg", '0,0,0', '0,96,25', '0,-3,0')

    @commands.hybrid_command(
        name="becomeanuke",
        description="Generate a nuke GIF from an avatar",
    )
    async def become_a_nuke(self, ctx: commands.Context, user: discord.User):
        await self.generate_gif(ctx, user, "/root/NyanStreamer/assets/models/Nuke.egg", '0,0,0', '0,0,45', '0,-4,0')
            
            
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
            
            
    #gay command
    @commands.hybrid_command(
        name="gay",
        description="make a user gay",
    )
    async def gay(self, ctx: Context, user: discord.User):
        avatar_url = str(user.avatar.url)
        logging.info(f"Received request to generate Gay image for avatar: {avatar_url}")
        
        try:
            gay_instance = self.endpoints.get("gay").Gay()
            if not gay_instance:
                raise Exception("John Oliver endpoint is missing.")
            
            image_data = gay_instance.generate([avatar_url], "", [], {})
            await ctx.send(file=discord.File(fp=image_data, filename="gay.png"))
        except Exception as e:
            logging.error(f"Failed to generate John Oliver image: {str(e)}")
            await ctx.send("Failed to generate the John Oliver image. Please try again.")
            
    @commands.hybrid_command(
        name="pat",
        description="pat a user",
    )
    async def pat(self, ctx: Context, user: discord.User):
        avatar_url = str(user.avatar.url)
        logging.info(f"Received request to generate Pat image for avatar: {avatar_url}")

        # Download the user's avatar image
        async with aiohttp.ClientSession() as session:
            async with session.get(avatar_url) as response:
                if response.status != 200:
                    return await ctx.send('Failed to download avatar.')
                image_content = await response.read()

        # Process the image
        source = BytesIO(image_content)
        dest = BytesIO()
        petpet.make(source, dest)
        dest.seek(0)

        # Send the processed image back to the channel
        file = discord.File(dest, filename="pat.gif")
        await ctx.send(file=file)


async def setup(bot):
    await bot.add_cog(Images(bot))
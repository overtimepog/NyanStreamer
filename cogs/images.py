import asyncio
from collections import defaultdict
import datetime
import json
import random
import re
import pytz
import requests
from discord import Color, Webhook, SyncWebhook
import aiohttp
import discord
from discord import Embed, app_commands
from discord.ext import commands, tasks
from discord.ext.commands import Context, has_permissions
import time

from helpers import battle, checks, db_manager, hunt, mine, search, bank, beg
from typing import List, Tuple
from discord.ext.commands.errors import CommandInvokeError
from num2words import num2words
from assets.endpoints import abandon, aborted, affect, airpods, america, armor, balloon, bed, bongocat, boo, brain, brazzers, byemom, cancer, changemymind, cheating, citation, communism, confusedcat, corporate, crab, cry, dab, dank, deepfry, delete, disability, doglemon, door, dream, egg, emergencymeeting, excuseme, expanddong, expandingwwe, facts, failure, fakenews, farmer, fedora, floor, fuck, garfield, gay, godwhy, goggles, hitler, humansgood, inator, invert, ipad, jail, justpretending, keepurdistance, kimborder, knowyourlocation, kowalski, laid, letmein, lick, madethis, magik, master, meme, note, nothing, obama, ohno, piccolo, plan, presentation, profile, quote, radialblur, rip, roblox, salty, satan, savehumanity, screams, shit, sickfilth, slap, slapsroof, sneakyfox, spank, stroke, surprised, sword, theoffice, thesearch, trash, trigger, tweet, ugly, unpopular, violence, violentsparks, vr, walking, wanted, warp, whodidthis, whothisis, yomomma, youtube
from discord import User, File
from aiohttp import ClientSession
from io import BytesIO
import concurrent.futures
from typing import Union

class Images(commands.Cog, name="images"):
    def __init__(self, bot):
        self.bot = bot
        self.session = ClientSession(loop=bot.loop)
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)

    
    @commands.hybrid_group(
    name="image",
    description="create funny images",
    invoke_without_command=True,
    aliases=["images", "meme", "memes"],
    )
    async def image(self, ctx: Context):
        if ctx.invoked_subcommand is None:
            #send an embed with the job commands
            await ctx.send_help(ctx.command)
            return
        
    @image.command(
    name="armor",
    description="nothing gets through here",
    )
    async def armor(self, ctx: Context, text: str):
        armor_instance = armor.Armor()
        image = await self.bot.loop.run_in_executor(self.executor, armor_instance.generate, [], text, [], "")

        # send the image
        await ctx.send(file=File(fp=image, filename="armor.png"))

    @image.command(
        name="bed",
        description="why do you hate me brother?",
    )
    async def bed(self, ctx: Context, user1: discord.User, user2: discord.User):
        bed_instance = bed.Bed()
        image = await self.bot.loop.run_in_executor(self.executor, bed_instance.generate, [user1.avatar.url, user2.avatar.url], "", [], "")

        # send the image
        await ctx.send(file=File(fp=image, filename="bed.png"))

    @image.command(
        name="crab",
        description="TIME TO RAVE",
    )
    async def crab(self, ctx: Context, text1: str, text2: str):
        crab_instance = crab.Crab()

        # Send a message indicating that the video is being generated
        message = await ctx.send("Generating your Rave... Please wait.")

        # Generate the video in a separate thread
        video = await self.bot.loop.run_in_executor(self.executor, crab_instance.generate, [], f"{text1},{text2}", [], "")

        # Edit the message to indicate that the video is ready
        await message.edit(content="Your Rave is ready!")

        # Send the video
        await ctx.send(file=discord.File(fp=video, filename="crab.mp4"))

    @image.command(
        name="deepfry",
        description="deepfry an image or user",
    )
    async def deepfry(self, ctx: Context, user: discord.User = None, image: discord.Attachment = None):
        fry_instance = deepfry.DeepFry()

        # Check the type of the image parameter
        if user is not None:
            # If a User is provided, use their avatar URL
            image_url = str(user.avatar.url)
        elif image is not None:
            # If an Attachment is provided, use its URL
            image_url = image.url
        else:
            # If neither is provided, raise an error
            raise commands.BadArgument("You must provide a user mention or an image attachment.")

        # Generate the deep fried image
        image = await self.bot.loop.run_in_executor(self.executor, fry_instance.generate, [image_url], "", [], "")

        await ctx.send(file=discord.File(fp=image, filename="deepfried.png"))


    @image.command(
        name="change_my_mind",
        description="change my mind",
        aliases=["cmm", "changemymind"],
    )
    async def change_my_mind(self, ctx: Context, *, text: str):
        change_my_mind_instance = changemymind.ChangeMyMind()
        image = await self.bot.loop.run_in_executor(self.executor, change_my_mind_instance.generate, [], text, [], "")
        await ctx.send(file=discord.File(fp=image, filename="changemymind.png"))

    @image.command(
        name="delete",
        description="delete an image or user",
    )
    async def delete(self, ctx: Context, user: discord.User = None, image: discord.Attachment = None):
        delete_instance = delete.Delete()

        # Check the type of the image parameter
        if user is not None:
            # If a User is provided, use their avatar URL
            image_url = str(user.avatar.url)
        elif image is not None:
            # If an Attachment is provided, use its URL
            image_url = image.url
        else:
            # If neither is provided, raise an error
            raise commands.BadArgument("You must provide a user mention or an image attachment.")

        # Generate the deep fried image
        image = await self.bot.loop.run_in_executor(self.executor, delete_instance.generate, [image_url], "", [], "")

        await ctx.send(file=discord.File(fp=image, filename="delete.png"))

async def setup(bot):
    await bot.add_cog(Images(bot))

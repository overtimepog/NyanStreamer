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

class Images(commands.Cog, name="images"):
    def __init__(self, bot):
        self.bot = bot
        self.session = ClientSession(loop=bot.loop)
    
    @commands.hybrid_group(
    name="image",
    description="create funny images",
    invoke_without_command=True,
    )
    async def image(self, ctx):
        if ctx.invoked_subcommand is None:
            #send an embed with the job commands
            await ctx.send_help(ctx.command)
            return

    @image.command(
        name="bed",
        description="why do you hate me brother?",
    )
    async def bed(self, ctx: Context, user1: discord.User, user2: discord.User):
        bed_instance = bed.Bed()
        image = bed_instance.generate([user1.avatar.url, user2.avatar.url], "", [], "")

        # send the image
        await ctx.send(file=File(fp=image, filename="image.png"))

    @image.command(
        name="crab",
        description="TIME TO RAVE",
    )
    async def crab(self, ctx: Context, text: str):
        parts = text.split(',')
        # Check if we have exactly two parts
        if len(parts) != 2:
            await ctx.send("You must provide exactly two strings separated by a comma.")
            return
        # Trim whitespace from the parts
        parts = [part.strip() for part in parts]
        # Join the parts back together with a comma
        text = ','.join(parts)
        # Now you can call the generate method with the properly formatted text
        crab_instance = crab.Crab()
        video = crab_instance.generate([], text, [], "")
        # Send the video
        await ctx.send(file=discord.File(fp=video, filename="crab.mp4"))

async def setup(bot):
    await bot.add_cog(Images(bot))

import asyncio
from collections import defaultdict
import datetime
import io
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
from typing import Union, Optional
import os
from petpetgif import petpet

def format_text(text):
    replacements = {
        "_": "__",
        " ": "_",
        "-": "--",
        "\n": "~n",
        "?": "~q",
        "&": "~a",
        "%": "~p",
        "#": "~h",
        "/": "~s",
        "\\": "~b",
        "<": "~l",
        ">": "~g",
        "\"": "''"
    }

    for key, value in replacements.items():
        text = text.replace(key, value)

    return text

class Images(commands.Cog, name="images"):
    def __init__(self, bot):
        self.bot = bot
        self.session = ClientSession(loop=bot.loop)
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)
        
    @commands.hybrid_command(
        name="abandon",
        description="abandon all hope",
    )
    async def abandon(self, ctx: Context, text: str):
        await ctx.defer()
        abandon_instance = abandon.Abandon()
        image = await self.bot.loop.run_in_executor(self.executor, abandon_instance.generate, [], text, [], "")

        # send the image
        await ctx.send(file=File(fp=image, filename="abandon.png"))

    @commands.hybrid_command(
        name="aborted",
        description="aborted mission",
    )
    async def aborted(self, ctx: Context, user: discord.User):
        await ctx.defer()
        aborted_instance = aborted.Aborted()
        image = await self.bot.loop.run_in_executor(self.executor, aborted_instance.generate, [user.avatar.url], "", [], "")

        # send the image
        await ctx.send(file=File(fp=image, filename="aborted.png"))

    @commands.hybrid_command(
        name="affect",
        description="no this doesnt affect my baby",
    )
    async def affect(self, ctx: Context, user: discord.User = None, image: discord.Attachment = None):
        await ctx.defer()
        affect_instance = affect.Affect()

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

        # Generate the image
        image = await self.bot.loop.run_in_executor(self.executor, affect_instance.generate, [image_url], "", [], "")

        await ctx.send(file=discord.File(fp=image, filename="affect.png"))

    @commands.hybrid_command(
        name="airpods",
        description="wear some airpods",
    )
    async def airpods(self, ctx: Context, user: discord.User):
        await ctx.defer()
        airpods_instance = airpods.Airpods()
        image = await self.bot.loop.run_in_executor(self.executor, airpods_instance.generate, [user.avatar.url], "", [], "")

        # send the image
        await ctx.send(file=File(fp=image, filename="airpods.gif"))

    @commands.hybrid_command(
        name="pet",
        description="pet a user",
    )
    async def pet(self, ctx: Context, user: discord.User):
        async with aiohttp.ClientSession() as session:
            async with session.get(user.avatar.url) as resp:
                image = await resp.read()
        source = BytesIO(image)  # file-like container to hold the emoji in memory
        dest = BytesIO()  # container to store the petpet gif in memory
        petpet.make(source, dest)
        dest.seek(0)  # set the file pointer back to the beginning so it doesn't upload a blank file.
        await ctx.send(file=discord.File(dest, filename=f"{user.name}Pet.gif"))

    @commands.hybrid_command(
        name="america",
        description="god bless this country",
    )
    async def america(self, ctx: Context, user: discord.User = None, image: discord.Attachment = None):
        await ctx.defer()
        america_instance = america.America()

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
        
        # Generate the image
        image = await self.bot.loop.run_in_executor(self.executor, america_instance.generate, [image_url], "", [], "")

        await ctx.send(file=discord.File(fp=image, filename="america.gif"))
        
    @commands.hybrid_command(
    name="armor",
    description="nothing gets through here",
    )
    async def armor(self, ctx: Context, text: str):
        await ctx.defer()
        armor_instance = armor.Armor()
        image = await self.bot.loop.run_in_executor(self.executor, armor_instance.generate, [], text, [], "")

        # send the image
        await ctx.send(file=File(fp=image, filename="armor.png"))

    @commands.hybrid_command(
        name="balloon",
        description="nothing gets through here",
    )
    async def balloon(self, ctx: Context, text1: str, text2: str):
        await ctx.defer()
        balloon_instance = balloon.Balloon()
        image = await self.bot.loop.run_in_executor(self.executor, balloon_instance.generate, [], f"{text1},{text2}", [], "")

        # send the image
        await ctx.send(file=File(fp=image, filename="balloon.png"))

    @commands.hybrid_command(
        name="bed",
        description="why do you hate me brother?",
    )
    async def bed(self, ctx: Context, user1: discord.User, user2: discord.User):
        await ctx.defer()
        bed_instance = bed.Bed()
        image = await self.bot.loop.run_in_executor(self.executor, bed_instance.generate, [user1.avatar.url, user2.avatar.url], "", [], "")

        # send the image
        await ctx.send(file=File(fp=image, filename="bed.png"))

    @commands.hybrid_command(
        name="crab",
        description="TIME TO RAVE",
    )
    async def crab(self, ctx: Context, text1: str, text2: str):
        await ctx.defer()
        crab_instance = crab.Crab()
        # Generate the video in a separate thread
        video = await self.bot.loop.run_in_executor(self.executor, crab_instance.generate, [], f"{text1},{text2}", [], "")
        # Send the video
        await ctx.send(file=discord.File(fp=video, filename="crab.mp4"))

    @commands.hybrid_command(
        name="custom",
        description="give top and bottom text to a user or image (Uses API)",
    )
    async def custom(self, ctx: Context, user: discord.User = None, image: discord.Attachment = None, url: str = None, top: str = None, bottom: str = None, format: str = None):
        await ctx.defer()
        if format is None and image is not None:
            format = image.content_type
        else:
            #get the format from the url, just check if its a png, jpeg, gif or webp, if not, default to png
            if url is not None:
                if url.__contains__(".png"):
                    format = "png"
                elif url.__contains__(".jpeg"):
                    format = "jpeg"
                elif url.__contains__(".gif"):
                    format = "gif"
                elif url.__contains__(".webp"):
                    format = "webp"
                else:
                    format = "png"
        if top is None:
            top = "_"
        if bottom is None:
            bottom = "_"
        # Check the type of the image parameter
        if user is not None:
            # If a User is provided, use their avatar URL
            image_url = str(user.avatar.url)
        elif image is not None:
            # If an Attachment is provided, use its URL
            image_url = image.url
        elif url is not None:
            # If a URL is provided, use it
            image_url = url
        else:
            # If neither is provided, raise an error
            raise commands.BadArgument("You must provide a user mention or an image attachment.")
        
        url = f"https://api.memegen.link/images/custom/{top}/{bottom}.{format}?background={image_url}&api_key=nu449chc96&watermark=nyanstreamer.lol"

        async with self.session.get(url) as resp:
            if resp.status != 200:
                return await ctx.send('Could not download file... The Api is down :(')
            data = io.BytesIO(await resp.read())
            await ctx.send(file=discord.File(data, f'custom.{format}'))

    @custom.autocomplete("format")
    async def custom_format(self, ctx: Context, argument):
        choices = []
        for format in ["png", "jpeg", "gif", "webp"]:
            if format.startswith(argument.lower()):
                choices.append(app_commands.Choice(name=format, value=format))
        return choices[:25]


    @commands.hybrid_command(
        name="dab",
        description="dab on them haters",
    )
    async def dab(self, ctx: Context, user: discord.User):
        await ctx.defer()
        dab_instance = dab.Dab()
        image = await self.bot.loop.run_in_executor(self.executor, dab_instance.generate, [user.avatar.url], "", [], "")

        # send the image
        await ctx.send(file=File(fp=image, filename="dab.png"))


    @commands.hybrid_command(
        name="deepfry",
        description="deepfry an image or user",
    )
    async def deepfry(self, ctx: Context, user: discord.User = None, image: discord.Attachment = None):
        await ctx.defer()
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

    @commands.hybrid_command(
        name="citation",
        description="citation needed",
    )
    async def citation(self, ctx: Context, title: str, text: str, footer: str):
        await ctx.defer()
        citation_instance = citation.Citation()
        image = await self.bot.loop.run_in_executor(self.executor, citation_instance.generate, [], f"{title},{text},{footer}", [], "")

        # send the image
        await ctx.send(file=File(fp=image, filename="citation.png"))


    @commands.hybrid_command(
        name="change_my_mind",
        description="change my mind",
        aliases=["cmm", "changemymind"],
    )
    async def change_my_mind(self, ctx: Context, *, text: str):
        await ctx.defer()
        change_my_mind_instance = changemymind.ChangeMyMind()
        image = await self.bot.loop.run_in_executor(self.executor, change_my_mind_instance.generate, [], text, [], "")
        await ctx.send(file=discord.File(fp=image, filename="changemymind.png"))

    @commands.hybrid_command(
        name="communism",
        description="I serve the soviet union",
    )
    async def communism(self, ctx: Context, user: discord.User):
        await ctx.defer()
        communism_instance = communism.Communism()
        image = await self.bot.loop.run_in_executor(self.executor, communism_instance.generate, [user.avatar.url], "", [], "")

        # send the image
        await ctx.send(file=File(fp=image, filename="communism.gif"))

    @commands.hybrid_command(
        name="delete",
        description="delete an image or user",
    )
    async def delete(self, ctx: Context, user: discord.User = None, image: discord.Attachment = None):
        await ctx.defer()
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

    @commands.hybrid_command(
        name="gru",
        description="I have a plan (Uses API)",
    )
    async def gru(self, ctx: Context, text1: str, text2: str, text3: str, text4: str = None, format: str = "png"):
        # Defer the interaction
        await ctx.defer()

        text1 = format_text(text1)
        text2 = format_text(text2)
        text3 = format_text(text3)
        if text4 is None:
            text4 = text3
        text4 = format_text(text4)
        url = f"https://api.memegen.link/images/gru/{text1}/{text2}/{text3}/{text4}.{format}?api_key=nu449chc96&watermark=nyanstreamer.lol"

        async with self.session.get(url) as resp:
            if resp.status != 200:
                return await ctx.send('Could not download file... The Api is down :(')
            data = io.BytesIO(await resp.read())
            await ctx.send(file=discord.File(data, f'gru.{format}'))

    @gru.autocomplete("format")
    async def gru_format(self, ctx: Context, argument):
        choices = []
        for format in ["png", "jpeg", "gif", "webp"]:
            if format.startswith(argument.lower()):
                choices.append(app_commands.Choice(name=format, value=format))
        return choices[:25]
    
    @commands.hybrid_command(
        name="jail",
        description="go to jail",
    )
    async def jail(self, ctx: Context, user: discord.User):
        await ctx.defer()
        jail_instance = jail.Jail()
        image = await self.bot.loop.run_in_executor(self.executor, jail_instance.generate, [user.avatar.url], "", [], "")

        # send the image
        await ctx.send(file=File(fp=image, filename="jail.png"))

    @commands.hybrid_command(
        name="gay",
        description="lit",
    )
    async def gay(self, ctx: Context, user: discord.User):
        await ctx.defer()
        gay_instance = gay.Gay()
        image = await self.bot.loop.run_in_executor(self.executor, gay_instance.generate, [user.avatar.url], "", [], "")

        # send the image
        await ctx.send(file=File(fp=image, filename="gay.png"))

    @commands.hybrid_command(
        name="buzz",
        description="To infinity and beyond! (Uses API)",
    )
    async def buzz(self, ctx: Context, top: str, bottom: str):
        # Defer the interaction
        await ctx.defer()

        top = format_text(top)
        bottom = format_text(bottom)
        url = f"https://api.memegen.link/images/buzz/{top}/{bottom}.gif?api_key=nu449chc96&watermark=nyanstreamer.lol"

        async with self.session.get(url) as resp:
            if resp.status != 200:
                return await ctx.send('Could not download file... The Api is down :(')
            data = io.BytesIO(await resp.read())
            await ctx.send(file=discord.File(data, 'buzz.gif'))

    @commands.hybrid_command(
        name="buttons",
        description="I cant Choose! (Uses API)",
    )
    async def buttons(self, ctx: Context, button1: str, button2: str):
        # Defer the interaction
        await ctx.defer()

        button1 = format_text(button1)
        button2 = format_text(button2)
        url = f"https://api.memegen.link/images/ds/{button1}/{button2}.png?api_key=nu449chc96&watermark=nyanstreamer.lol"

        async with self.session.get(url) as resp:
            if resp.status != 200:
                return await ctx.send('Could not download file... The Api is down :(')
            data = io.BytesIO(await resp.read())
            await ctx.send(file=discord.File(data, 'buttons.png'))


    @commands.hybrid_command(
        name="butterfly",
        description="Is this a butterfly? (Uses API)",
    )
    async def butterfly(self, ctx: Context, text: str, butterfly: discord.User, person: discord.User = None, ):
        await ctx.defer()
        location_x = "0.333"
        location_y = "0.3"
        scale = "0.5"

        if person is None:
            person = ctx.author
        # Check the type of the butterfly parameter
        if butterfly is not None:
            # If a User is provided, use their avatar URL
            butterfly_content = "_"
            style = str(butterfly.avatar.url)
        
        else:
            # If neither is provided, raise an error
            await ctx.send("You must provide text, a user mention or an image attachment for the butterfly.")
            raise commands.BadArgument("You must provide a text, user mention or an image attachment for the butterfly.")

        # Format the person and text parameters
        person = format_text(person)
        text = format_text(text)

        # Generate the image URL for the first part
        url = f"https://api.memegen.link/images/pigeon/_/{butterfly_content}/{text}.png"
        if style is not None:
            url += f"?style={style}"

        #now generate the second part where the user avatar is layered ontop of the first part
        url_full = f"https://api.memegen.link/images/custom/_.png?background={url}&style={person.avatar.url}&center={location_x},{location_y}&scale={scale}"
        
        #then we add the api and the watermark
        url_full += "&api_key=nu449chc96&watermark=nyanstreamer.lol"
        # Send the image
        async with self.session.get(url_full) as resp:
            if resp.status != 200:
                return await ctx.send('Could not download file... The Api is down :(')
            data = io.BytesIO(await resp.read())
            await ctx.send(file=discord.File(data, 'butterfly.png'))

    @commands.hybrid_command(
        name="expand_dong",
        description="my ding dong",
    )
    async def expand_dong(self, ctx: Context, text: str):
        await ctx.defer()
        expand_dong_instance = expanddong.ExpandDong()
        image = await self.bot.loop.run_in_executor(self.executor, expand_dong_instance.generate, [], text, [], "")

        # send the image
        await ctx.send(file=File(fp=image, filename=f"{text}.png"))

    @commands.hybrid_command(
        name="genius",
        description="smart af (Uses API)",
    )
    async def genius(self, ctx: Context, text: str):
        await ctx.defer()

        text = format_text(text)
        url = f"https://api.memegen.link/images/rollsafe/{text}.gif?layout=top&api_key=nu449chc96&watermark=nyanstreamer.lol"

        async with self.session.get(url) as resp:
            if resp.status != 200:
                return await ctx.send('Could not download file... The Api is down :(')
            data = io.BytesIO(await resp.read())
            await ctx.send(file=discord.File(data, 'genius.gif'))

    @commands.hybrid_command(
        name="bongo_cat",
        description="bongo catify an image or user",
    )
    async def bongo_cat(self, ctx: Context, user: discord.User = None, image: discord.Attachment = None):
        await ctx.defer()
        bongo_cat_instance = bongocat.BongoCat()

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
        image = await self.bot.loop.run_in_executor(self.executor, bongo_cat_instance.generate, [image_url], "", [], "")

        await ctx.send(file=discord.File(fp=image, filename="bongocat.png"))

    @commands.hybrid_command(
        name="tweet",
        description="tweet something",
    )
    async def tweet(self, ctx: Context, user: discord.User, text: str):
        await ctx.defer()
        tweet_instance = tweet.Tweet()
        image = await self.bot.loop.run_in_executor(self.executor, tweet_instance.generate, [user.avatar.url], text, [user.name], "")

        # send the image
        await ctx.send(file=File(fp=image, filename="tweet.png"))

    @commands.hybrid_command(
        name="wanted",
        description="just kidding nobody wants you",
    )
    async def wanted(self, ctx: Context, user: discord.User):
        await ctx.defer()
        wanted_instance = wanted.Wanted()
        image = await self.bot.loop.run_in_executor(self.executor, wanted_instance.generate, [user.avatar.url], "", [], "")
        # send the image
        await ctx.send(file=File(fp=image, filename="wanted.png"))

    @commands.hybrid_command(
        name="whodidthis",
        description="who did this",
    )
    async def whodidthis(self, ctx: Context, user: discord.User):
        await ctx.defer()
        whodidthis_instance = whodidthis.Whodidthis()
        image = await self.bot.loop.run_in_executor(self.executor, whodidthis_instance.generate, [user.avatar.url], "", [], "")
        # send the image
        await ctx.send(file=File(fp=image, filename="whodidthis.png"))

    @commands.hybrid_command(
        name="whothisis",
        description="who is this",
    )
    async def whothisis(self, ctx: Context, user: discord.User, text: str):
        await ctx.defer()
        whothisis_instance = whothisis.WhoThisIs()
        image = await self.bot.loop.run_in_executor(self.executor, whothisis_instance.generate, [user.avatar.url], f"{text}", [], "")
        # send the image
        await ctx.send(file=File(fp=image, filename="whothisis.png"))

    @commands.hybrid_command(
        name="youtube",
        description="just dont edit it",
    )
    async def youtube(self, ctx: Context, user: discord.User, text: str):
        await ctx.defer()
        youtube_instance = youtube.Youtube()
        image = await self.bot.loop.run_in_executor(self.executor, youtube_instance.generate, [user.avatar.url], f"{text}", [user.name], "")
        # send the image
        await ctx.send(file=File(fp=image, filename="youtube.png"))

    @commands.hybrid_command(
        name="kowalski",
        description="analysis",
    )
    async def kowalski(self, ctx: Context, text: str):
        await ctx.defer()
        kowalski_instance = kowalski.Kowalski()
        image = await self.bot.loop.run_in_executor(self.executor, kowalski_instance.generate, [], f"{text}", [], "")
        # send the image
        await ctx.send(file=File(fp=image, filename="kowalski.gif"))

    @commands.hybrid_command(
        name="trigger",
        description="triggered",
    )
    async def trigger(self, ctx: Context, user: discord.User):
        await ctx.defer()
        trigger_instance = trigger.Trigger()
        image = await self.bot.loop.run_in_executor(self.executor, trigger_instance.generate, [user.avatar.url], "", [], "")
        # send the image
        await ctx.send(file=File(fp=image, filename="trigger.gif"))

    #tweet
    @commands.hybrid_command(
        name="tweet",
        description="tweet something from a user",
    )
    async def tweet(self, ctx: Context, user: discord.User, text: str):
        await ctx.defer()
        tweet_instance = tweet.Tweet()
        image = await self.bot.loop.run_in_executor(self.executor, tweet_instance.generate, [user.avatar.url], f"{text}", [user.name], "")
        # send the image
        await ctx.send(file=File(fp=image, filename="tweet.png"))

async def setup(bot):
    await bot.add_cog(Images(bot))

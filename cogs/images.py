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
import sys
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
from PIL import Image
from urllib.parse import quote
from jeyyapi import JeyyAPIClient
import subprocess
import fcntl
client = JeyyAPIClient('6COJCCHO74OJ2CPM6GRJ4C9O6OS3G.9PSM2RH0ADQ74PB1DLIN4.FOauZ8Gi-J7wAuWDj_hH-g')
    # Define a function that wraps around the spinning_model function
Nyan_Api_Key = '2Odpb9365gSmA3RXtQa0NGVjS8-QUGBLKxsty8EKM00'


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

async def replace_mentions_with_names(ctx: Context, text: str) -> str:
    # Find all mentions in the format <@ID>
    mentions = re.findall(r'<@(\d+)>', text)
    for mention in mentions:
        # Fetch the user using the ID
        user = await ctx.guild.fetch_member(int(mention))
        # Replace the mention with the user's name
        text = text.replace(f'<@{mention}>', user.name + ' ').replace('  ', ' ')
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
    async def affect(self, ctx: Context, user: discord.User):
        await ctx.defer()
        affect_instance = affect.Affect()
        image_url = str(user.avatar.url)

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
        name="pat",
        aliases=["headpat"],
        description="give a user some head scratches",
    )
    async def pat(self, ctx: Context, user: discord.User):
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
    async def america(self, ctx: Context, user: discord.User):
        await ctx.defer()
        america_instance = america.America()
        image_url = str(user.avatar.url)
        
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
        image = await self.bot.loop.run_in_executor(self.executor, balloon_instance.generate, [], f"{text1}, {text2}", [], "")

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
        description="give top and bottom text to a user or image ",
    )
    async def custom(self, ctx: Context, user: discord.User = None, image: discord.Attachment = None, url: str = None, top: str = None, bottom: str = None, format: str = None):
        await ctx.defer()
        if format is None:
            format = "png"
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
        name="undertale",
        description="generate an undertale text box",
    )
    async def undertale(self, ctx: Context, text: str, user: discord.User = None, character: str = None):
        #https://www.demirramon.com/gen/undertale_text_box.gif?animate=true&character=custom&url=https://cdn.discordapp.com/attachments/1113231948027003011/1133155741407121508/balloon.png&message=omg%20I%20love%20nuts
        await ctx.defer()
        if character is None:
            character = "custom"
        if user is None:
            user = ctx.author

        text = quote(text)
        url = f"https://www.demirramon.com/gen/undertale_text_box.gif?animate=true&character={character}&url={user.avatar.url}&message={text}"

        async with self.session.get(url) as resp:
            if resp.status != 200:
                return await ctx.send('Could not Generate Image... the Character you provided is not valid')
            data = io.BytesIO(await resp.read())
            await ctx.send(file=discord.File(data, 'undertale.gif'))


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
    async def deepfry(self, ctx: Context, user: discord.User):
        await ctx.defer()
        fry_instance = deepfry.DeepFry()
        image_url = str(user.avatar.url)

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

    #eject command
    @commands.hybrid_command(
        name="eject",
        description="eject a user if they're sus",
    )
    async def eject(self, ctx: Context, user: discord.User, imposter: str = None):
        #open config .json
        with open("config.json") as file:
            data = json.load(file)
            
        #get the api key
        sr_api_key = data["SRA-KEY"]

        if imposter is None:
            outcome = random.choice(["true", "false"])
        elif imposter == "True":
            outcome = "true"
        elif imposter == "False":
            outcome = "false"

        await ctx.defer()
        url = f"https://some-random-api.com/premium/amongus?avatar={user.avatar.url}&key={sr_api_key}&username={user.display_name[0:35]}&imposter={outcome}"
        async with self.session.get(url) as resp:
            if resp.status != 200:
                return await ctx.send('Could not download file... The Api is down :(')
            data = io.BytesIO(await resp.read())
            await ctx.send(file=File(fp=data, filename="eject.gif"))

    #give imposter autocomplete for eject command of either true or false
    @eject.autocomplete("imposter")
    async def eject_imposter(self, ctx: Context, argument):
        choices = []
        for imposter in ["True", "False"]:
            if imposter.startswith(argument.lower()):
                choices.append(app_commands.Choice(name=imposter, value=imposter))
        return choices[:25]

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
        description="delete a user",
    )
    async def delete(self, ctx: Context, user: discord.User):
        await ctx.defer()
        delete_instance = delete.Delete()
        image_url = str(user.avatar.url)

        # Generate the deep fried image
        image = await self.bot.loop.run_in_executor(self.executor, delete_instance.generate, [image_url], "", [], "")

        await ctx.send(file=discord.File(fp=image, filename="delete.png"))

    @commands.hybrid_command(
        name="gru",
        description="I have a plan ",
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
        description="To infinity and beyond! ",
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
        description="I cant Choose! ",
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
        description="smart af ",
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
    async def bongo_cat(self, ctx: Context, user: discord.User):
        await ctx.defer()
        bongo_cat_instance = bongocat.BongoCat()
        image_url = str(user.avatar.url)

        # Generate the deep fried image
        image = await self.bot.loop.run_in_executor(self.executor, bongo_cat_instance.generate, [image_url], "", [], "")

        await ctx.send(file=discord.File(fp=image, filename="bongocat.png"))

    @commands.hybrid_command(
        name="tweet",
        description="tweet something",
    )
    async def tweet(self, ctx: Context, user: discord.User, text: str):
        avatar_url = str(user.avatar.url)
        await ctx.defer()
        async with aiohttp.ClientSession() as session:
            async with session.get(f"http://nyanstreamer.lol/image/tweet?avatar_url={avatar_url}&text={quote(text)}&username={user.name}") as response:
                if response.status == 200:
                    image_data = await response.read()
                    await ctx.send(file=discord.File(io.BytesIO(image_data), filename="tweet.png"))
                else:
                    # Handle non-image responses here
                    text_data = await response.text()
                    await ctx.send(f"Error: {text_data}", ephemeral=True)

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
        avatar_url = str(user.avatar.url)
        await ctx.defer()
        async with aiohttp.ClientSession() as session:
            async with session.get(f"http://nyanstreamer.lol/image/trigger?avatar_url={avatar_url}") as response:
                if response.status == 200:
                    image_data = await response.read()
                    await ctx.send(file=discord.File(io.BytesIO(image_data), filename="triggered.gif"))
                else:
                    # Handle non-image responses here
                    text_data = await response.text()
                    await ctx.send(f"Error: {text_data}", ephemeral=True)

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
        
    @commands.hybrid_command(
        name="polishcow",
        description="become polish cow ",
        aliases=["polish_cow", "polish-cow", "cow"],
    )
    async def polishcow(self, ctx: Context, user: discord.User):
        await ctx.defer()
        avatar = user.avatar.url
        image = await client.cow(avatar)
        await ctx.send(file=File(fp=image, filename="polishcow.gif"))
    
    @commands.hybrid_command(
        name="clock",
        description="what time is it?, become a clock ",
    )
    async def clock(self, ctx: Context, user: discord.User):
        await ctx.defer()
        avatar = user.avatar.url
        image = await client.clock(avatar)
        await ctx.send(file=File(fp=image, filename="clock.gif"))
        
    #globe
    @commands.hybrid_command(
        name="globe",
        description="Mr 305",
    )
    async def globe(self, ctx: Context, user: discord.User):
        await ctx.defer()
        avatar = user.avatar.url
        image = await client.globe(avatar)
        await ctx.send(file=File(fp=image, filename="globe.gif"))
        
    #wheel, it has a potential 6 args, with 2 needed and 4 optional
    @commands.hybrid_command(
        name="wheel",
        description="spin the wheel",
    )
    #label the option option1 through option6
    async def wheel(self, ctx: Context, question: str, option1: str, option2: str, option3: str = None, option4: str = None, option5: str = None, option6: str = None):
        await ctx.defer()
        #create a list of all the options that are not None
        options = [option1, option2, option3, option4, option5, option6]
        options = [i for i in options if i is not None]
        #if there are less than 2 options, raise an error
        if len(options) < 2:
            raise commands.BadArgument("You must provide at least 2 options")
        #if there are more than 6 options, raise an error
        if len(options) > 6:
            raise commands.BadArgument("You can only provide 6 options")
        
        wheel = await client.wheel(options)
        #print(image)
            # Create a Discord embed for the GIF wheel
        #title the question
        question = await replace_mentions_with_names(ctx, question)
        option1 = await replace_mentions_with_names(ctx, option1)
        option2 = await replace_mentions_with_names(ctx, option2)
        if option3:
            option3 = await replace_mentions_with_names(ctx, option3)
        if option4:
            option4 = await replace_mentions_with_names(ctx, option4)
        if option5:
            option5 = await replace_mentions_with_names(ctx, option5)
        if option6:
            option6 = await replace_mentions_with_names(ctx, option6)

        question = question.title()

        desc = wheel['desc'].replace(" :\t\t", " ")
        embed_gif = Embed(
            title=f"**{question}** - {ctx.author.name}",
            description=f"**{desc}**"
        )
        embed_gif.set_image(url=wheel['gif_wheel'])

        # Send the GIF wheel embed to the channel
        message = await ctx.send(embed=embed_gif)

        # Wait for the specified time minus 0.5 seconds
        await asyncio.sleep(wheel['time'] - 0.5)

        # Create a Discord embed for the result
        embed_result = Embed(
            title=f"**{question}** - {ctx.author.name}",
            description=f"**{wheel['result_color_emoji']} {wheel['result']}**",
        )
        embed_result.set_image(url=wheel['result_img'])
        # Send the result embed to the channel
        await message.edit(embed=embed_result)
        
    #matrix
    @commands.hybrid_command(
        name="matrix",
        description="become the matrix",
    )
    async def matrix(self, ctx: Context, user: discord.User):
        await ctx.defer()
        avatar = user.avatar.url
        image = await client.matrix(avatar)
        await ctx.send(file=File(fp=image, filename="matrix.gif"))
        
    #balls
    @commands.hybrid_command(
        name="balls",
        description="man I love those",
    )
    async def balls(self, ctx: Context, user: discord.User):
        await ctx.defer()
        avatar = user.avatar.url
        image = await client.balls(avatar)
        await ctx.send(file=File(fp=image, filename="balls.gif"))
        
    #billboard
    @commands.hybrid_command(
        name="billboard",
        description="become a billboard",
    )
    async def billboard(self, ctx: Context, user: discord.User):
        await ctx.defer()
        avatar = user.avatar.url
        image = await client.billboard(avatar)
        await ctx.send(file=File(fp=image, filename="billboard.png"))
        
    #heart locket
    @commands.hybrid_command(
        name="heartlocket",
        description="become a heart locket",
    )
    async def heartlocket(self, ctx: Context, user: discord.User):
        await ctx.defer()
        avatar = user.avatar.url
        image = await client.heart_locket(avatar, avatar)
        await ctx.send(file=File(fp=image, filename="heartlocket.gif"))
    
    #pizza
    @commands.hybrid_command(
        name="pizza",
        description="become a pizza",
    )
    async def pizza(self, ctx: Context, user: discord.User):
        await ctx.defer()
        avatar = user.avatar.url
        image = await client.pizza(avatar)
        await ctx.send(file=File(fp=image, filename="pizza.png"))
        
    #zonk
    @commands.hybrid_command(
        name="zonk",
        description="zonk",
    )
    async def zonk(self, ctx: Context, user: discord.User):
        await ctx.defer()
        avatar = user.avatar.url
        image = await client.zonk(avatar)
        await ctx.send(file=File(fp=image, filename="zonk.gif"))

    #stonks
    @commands.hybrid_command(
        name="salty",
        description="salty fr",
    )
    async def salty(self, ctx: Context, user: discord.User):
        avatar_url = str(user.avatar.url)
        await ctx.defer()
        async with aiohttp.ClientSession() as session:
            async with session.get(f"http://nyanstreamer.lol/image/salty?avatar_url={avatar_url}") as response:
                if response.status == 200:
                    image_data = await response.read()
                    await ctx.send(file=discord.File(io.BytesIO(image_data), filename="salt.png"))
                else:
                    # Handle non-image responses here
                    text_data = await response.text()
                    await ctx.send(f"Error: {text_data}", ephemeral=True)
        
    # chair command
    @commands.hybrid_command(
        name="chair",
        description="become a chair",
    )
    async def chair(self, ctx: Context, user: discord.User):
        avatar_url = str(user.avatar.url)
        await ctx.defer()
        headers = {
            "Authorization": f"Bearer {Nyan_Api_Key}"
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(f"http://nyanstreamer.lol/3d/chair?avatar_url={avatar_url}", headers=headers) as response:
                if response.status == 200:
                    gif_data = await response.read()
                    await ctx.send(file=discord.File(io.BytesIO(gif_data), filename=f"{user.name}_chair.gif"))
                else:
                    # Handle non-image responses here
                    text_data = await response.text()
                    await ctx.send(f"Error: {text_data}", ephemeral=True)

    #async def chair(self, ctx: Context, user: discord.User):
    #    await ctx.defer()
    #    image_url = user.avatar.url
    #    frames = 24
    #    filename = f"{user.name}_chair"
    #    #model_path = "/Users/overtime/Documents/GitHub/NyanStreamer/assets/models/Chair.egg"
    #    model_path = "/root/NyanStreamer/assets/models/Chair.egg"
    #    #check if the model exists
    #    if not os.path.exists(model_path):
    #        await ctx.send("The chair model is missing. Please try again later.")
    #        return
    #    
    #    subprocess.Popen([sys.executable, 'helpers/spinning_model_maker.py', model_path, image_url, str(frames), filename, '0,0,0', '0,96,25', '0,-3,0'])
    #    timeout = 300  # 5 minutes, adjust as needed
    #    check_interval = 1  # check every second
    #    elapsed_time = 0
#
    #    gif_path = filename + ".gif"
#
    #    while elapsed_time < timeout:
    #        if os.path.exists(gif_path):
    #            with open(gif_path, 'rb') as f:
    #                try:
    #                    fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)  # Try to acquire an exclusive lock
    #                    fcntl.flock(f, fcntl.LOCK_UN)  # Release the lock immediately
    #                    break  # If we got here, it means we acquired the lock, so the file is ready
    #                except IOError:
    #                    pass  # Couldn't acquire the lock, so the file is still being written
    #        time.sleep(check_interval)
    #        elapsed_time += check_interval
#
    #    if os.path.exists(gif_path):
    #        print(f"Sending {gif_path}")
    #        await ctx.send(file=discord.File(gif_path))
    #        os.remove(gif_path)
    #    else:
    #        await ctx.send("Failed to generate the chair GIF. Please try again.")


    #can command
    @commands.hybrid_command(
        name="can",
        description="Id love a sip of that",
        aliases=["soda", "soda_can", "energy_drink", "energydrink"]
    )
    async def can(self, ctx: Context, user: discord.User):
        avatar_url = str(user.avatar.url)
        await ctx.defer()
        headers = {
            "Authorization": f"Bearer {Nyan_Api_Key}"
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(f"http://nyanstreamer.lol/3d/can?avatar_url={avatar_url}", headers=headers) as response:
                if response.status == 200:
                    gif_data = await response.read()
                    await ctx.send(file=discord.File(io.BytesIO(gif_data), filename=f"{user.name}_can.gif"))
                else:
                    # Handle non-image responses here
                    text_data = await response.text()
                    await ctx.send(f"Error: {text_data}", ephemeral=True)

        #await ctx.defer()
        #image_url = user.avatar.url
        #frames = 24
        #filename = f"{user.name}_can"
        ##model_path = "/Users/overtime/Documents/GitHub/NyanStreamer/assets/models/Can.egg"
        #model_path = "/root/NyanStreamer/assets/models/Can.egg"
        ##check if the model exists
        #if not os.path.exists(model_path):
        #    await ctx.send("The can model is missing. Please try again later.")
        #    return
        #
        #subprocess.Popen([sys.executable, 'helpers/spinning_model_maker.py', model_path, image_url, str(frames), filename, '0,0,-0.85', '0,100,0', '0,-5,0'])
        #timeout = 300  # 5 minutes, adjust as needed
        #check_interval = 1  # check every second
        #elapsed_time = 0
#
        #gif_path = filename + ".gif"
#
        #while elapsed_time < timeout:
        #    if os.path.exists(gif_path):
        #        with open(gif_path, 'rb') as f:
        #            try:
        #                fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)  # Try to acquire an exclusive lock
        #                fcntl.flock(f, fcntl.LOCK_UN)  # Release the lock immediately
        #                break  # If we got here, it means we acquired the lock, so the file is ready
        #            except IOError:
        #                pass  # Couldn't acquire the lock, so the file is still being written
        #    time.sleep(check_interval)
        #    elapsed_time += check_interval
#
        #if os.path.exists(gif_path):
        #    print(f"Sending {gif_path}")
        #    await ctx.send(file=discord.File(gif_path))
        #    os.remove(gif_path)
        #else:
        #    await ctx.send("Failed to generate the can GIF. Please try again.")
            
    #nuke command
    @commands.hybrid_command(
        name="nuke",
        description="become a nuke",
    )
    async def nuke(self, ctx: Context, user: discord.User):
        avatar_url = str(user.avatar.url)
        await ctx.defer()
        headers = {
            "Authorization": f"Bearer {Nyan_Api_Key}"
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(f"http://nyanstreamer.lol/3d/nuke?avatar_url={avatar_url}", headers=headers) as response:
                if response.status == 200:
                    gif_data = await response.read()
                    await ctx.send(file=discord.File(io.BytesIO(gif_data), filename=f"{user.name}_nuke.gif"))
                else:
                    # Handle non-image responses here
                    text_data = await response.text()
                    await ctx.send(f"Error: {text_data}", ephemeral=True)

    #async def nuke(self, ctx: Context, user: discord.User):
    #    await ctx.defer()
    #    image_url = user.avatar.url
    #    frames = 24
    #    filename = f"{user.name}_nuke"
    #    #model_path = "/Users/overtime/Documents/GitHub/NyanStreamer/assets/models/Nuke.egg"
    #    model_path = "/root/NyanStreamer/assets/models/Nuke.egg"
    #    #check if the model exists
    #    if not os.path.exists(model_path):
    #        await ctx.send("The nuke model is missing. Please try again later.")
    #        return
    #    
    #    subprocess.Popen([sys.executable, 'helpers/spinning_model_maker.py', model_path, image_url, str(frames), filename, '0,0,0', '0,0,45', '0,-4,0'])
    #    timeout = 300  # 5 minutes, adjust as needed
    #    check_interval = 1  # check every second
    #    elapsed_time = 0
#
    #    gif_path = filename + ".gif"
#
    #    while elapsed_time < timeout:
    #        if os.path.exists(gif_path):
    #            with open(gif_path, 'rb') as f:
    #                try:
    #                    fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)  # Try to acquire an exclusive lock
    #                    fcntl.flock(f, fcntl.LOCK_UN)  # Release the lock immediately
    #                    break  # If we got here, it means we acquired the lock, so the file is ready
    #                except IOError:
    #                    pass  # Couldn't acquire the lock, so the file is still being written
    #        time.sleep(check_interval)
    #        elapsed_time += check_interval
#
    #    if os.path.exists(gif_path):
    #        print(f"Sending {gif_path}")
    #        await ctx.send(file=discord.File(gif_path))
    #        os.remove(gif_path)
    #    else:
    #        await ctx.send("Failed to generate the nuke GIF. Please try again.")
async def setup(bot):
    await bot.add_cog(Images(bot))

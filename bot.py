"""
Copyright © Krypton 2022 - https://github.com/kkrypt0nn (https://krypton.ninja)
Description:
This is a template to create your own discord bot in python.

Version: 5.4
"""

import asyncio
import datetime
import json
import os
import platform
import random
import sys
import subprocess
import requests

import aiosqlite
import discord
from discord.ext import commands, tasks
from discord.ext.commands import Bot, Context
from discord.ext.commands import Context, has_permissions

from helpers import battle, checks, db_manager, hunt, mine

import exceptions
from helpers import db_manager
import twitch

cash = "<:cash:1077573941515792384>"
if not os.path.isfile("config.json"):
    sys.exit("'config.json' not found! Please add it and try again.")
else:
    with open("config.json") as file:
        config = json.load(file)

"""	
Setup bot intents (events restrictions)
For more information about intents, please go to the following websites:
https://discordpy.readthedocs.io/en/latest/intents.html
https://discordpy.readthedocs.io/en/latest/intents.html#privileged-intents


Default Intents:
intents.bans = True
intents.dm_messages = True
intents.dm_reactions = True
intents.dm_typing = True
intents.emojis = True
intents.emojis_and_stickers = True
intents.guild_messages = True
intents.guild_reactions = True
intents.guild_scheduled_events = True
intents.guild_typing = True
intents.guilds = True
intents.integrations = True
intents.invites = True
intents.messages = True # `message_content` is required to get the content of the messages
intents.reactions = True
intents.typing = True
intents.voice_states = True
intents.webhooks = True

Privileged Intents (Needs to be enabled on developer portal of Discord), please use them only if you need them:
intents.members = True
intents.message_content = True
intents.presences = True
"""

intents = discord.Intents.all()

"""
Uncomment this if you don't want to use prefix (normal) commands.
It is recommended to use slash commands and therefore not use prefix commands.

If you want to use prefix commands, make sure to also enable the intent below in the Discord developer portal.
"""
intents.message_content = True

bot = Bot(command_prefix=commands.when_mentioned_or(
    config["prefix"]), intents=intents, help_command=None)


async def init_db():
    async with aiosqlite.connect("database/database.db") as db:
        with open("database/schema.sql") as file:
            await db.executescript(file.read())
        await db.commit()


"""
Create a bot variable to access the config file in cogs so that you don't need to import it every time.

The config is available using the following code:
- bot.config # In this file
- self.bot.config # In cogs
"""
bot.config = config
    

#every 12 hours the shop will reset, create a task to do this
#every 5 hours a structure will spawn in the channel named "dankstreamer-structures"
@tasks.loop(minutes=90)
async def structure_spawn_task() -> None:       
    #get the structures channel
    for bot_guild in bot.guilds:
        #if bot_guild.id == 1070882685855211641:
        #    print("Skipping " + bot_guild.name + " because it's the Connections server")
        #    continue
        #reset the guilds current structure
        channel = discord.utils.get(bot_guild.text_channels, topic="dankstreamer-structures")
        if channel is None:
            #print("A channel with the topic dankstreamer-structures does not exist in " + bot_guild.name)
            continue
        
        if await db_manager.get_current_structure(bot_guild.id) is not None:
            #print("A structure is already spawned in " + bot_guild.name)
            continue
        
        #get a random structure
        structureschoices = await db_manager.get_structures()
        structure = random.choice(structureschoices)
        structureid = structure[0]
        structure_name = structure[1]
        print("Spawned " + structure_name + " in " + bot_guild.name)
        #send the structure
        #message = await channel.send(content=f"{structure_name} has Appeared")
            #print(structure_outcomes)
        #get the strucure info using the db_manager
        structure_info = await db_manager.get_structure(structureid)
        #get the structure name
        structure_name = structure_info[1]
        #get the structure description
        structure_description = structure_info[3]
        #get the structure image
        structure_image = structure_info[2]
        #creare an embed to show the structure info
        embed = discord.Embed(title=f"{structure_name}", description=f"{structure_description}")
        embed.set_image(url=f"{structure_image}")
        embed.set_footer(text=f"/explore structure:{structureid}")
        await channel.send(embed=embed)
        await db_manager.edit_current_structure(bot_guild.id, structureid)

@tasks.loop(minutes=30)
async def mob_spawn_task() -> None:
    mobs = await db_manager.get_all_enemies()
    for bot_guild in bot.guilds:
        #if bot_guild.id == 1070882685855211641:
        #    print("Skipping " + bot_guild.name + " because it's the Connections server")
        #    continue
        #reset the guilds current structure
        channel = discord.utils.get(bot_guild.text_channels, topic="dankstreamer-structures")
        if channel is None:
            #print("A channel with the topic dankstreamer-structures does not exist in " + bot_guild.name)
            continue
        
        if await db_manager.get_current_structure(bot_guild.id) is not None:
            #print("A structure is already spawned in " + bot_guild.name)
            continue
        #get all the mobs that can spawn

        #get a random mob
        mob = random.choice(mobs)
        mobid = mob[0]
        mob_name = mob[1]
        #get the current spawned mobs
        current_mob = await db_manager.get_current_spawn(bot_guild.id)
        if current_mob is not None:
            print("A mob is already spawned in " + bot_guild.name)
            continue
        await battle.spawn_monster(channel, mobid)
        print("Spawned " + mob_name + " in " + bot_guild.name)





@tasks.loop(minutes=1.0)
async def status_task() -> None:
    """
    Setup the game status task of the bot
    """
    statuses = ["With Streamers!", "/help", "d!help", "/start", "d!start"]
    await bot.change_presence(activity=discord.Game(random.choice(statuses)))
    
#create a task to regenerate the twitch credentials and save them to the database, every 5 days

@bot.event
async def on_message(message: discord.Message) -> None:
    """
    The code in this event is executed every time someone sends a message, with or without the prefix

    :param message: The message that was sent.
    """
    #wait for a different message from the webhook
    if message.author == bot.user or message.author.bot:
        return
    await bot.process_commands(message)

    #if the channel is the connections channel, two messages will be seen, the first will have the users ID after the word DISCORD ID:, and the second will have the users twitch ID after the word TWITCH ID:, this will be used to connect the twitch account to the discord account, so grab the first message, wait for the second message, and then connect the two accounts
    #if the message was sent from this webhook, run the code below



@bot.event
async def on_command_completion(context: Context) -> None:
    """
    The code in this event is executed every time a normal command has been *successfully* executed
    :param context: The context of the command that has been executed.
    """
    full_command_name = context.command.qualified_name
    split = full_command_name.split(" ")
    executed_command = str(split[0])
    if context.guild is not None:
        print(
            f"Executed {executed_command} command in {context.guild.name} (ID: {context.guild.id}) by {context.author} (ID: {context.author.id})")
    else:
        print(
            f"Executed {executed_command} command by {context.author} (ID: {context.author.id}) in DMs")


@bot.event
async def on_command_error(context: Context, error) -> None:
    """
    The code in this event is executed every time a normal valid command catches an error
    :param context: The context of the normal command that failed executing.
    :param error: The error that has been faced.
    """
    if isinstance(error, commands.CommandOnCooldown):
        minutes, seconds = divmod(error.retry_after, 60)
        hours, minutes = divmod(minutes, 60)
        hours = hours % 24
        embed = discord.Embed(
            title="Hey, please slow down!",
            description=f"You can use this command again in {f'{round(hours)} hours' if round(hours) > 0 else ''} {f'{round(minutes)} minutes' if round(minutes) > 0 else ''} {f'{round(seconds)} seconds' if round(seconds) > 0 else ''}.",
            color=0xE02B2B
        )
        await context.send(embed=embed)
    elif isinstance(error, exceptions.UserBlacklisted):
        """
        The code here will only execute if the error is an instance of 'UserBlacklisted', which can occur when using
        the @checks.not_blacklisted() check in your command, or you can raise the error by yourself.
        """
        embed = discord.Embed(
            title="Error!",
            description="You are blacklisted from using the bot.",
            color=0xE02B2B
        )
        await context.send(embed=embed)
    elif isinstance(error, exceptions.UserNotOwner):
        """
        Same as above, just for the @checks.is_owner() check.
        """
        embed = discord.Embed(
            title="Error!",
            description="You are not the owner of the bot!",
            color=0xE02B2B
        )
        await context.send(embed=embed)
    elif isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(
            title="Error!",
            description="You are missing the permission(s) `" + ", ".join(
                error.missing_permissions) + "` to execute this command!",
            color=0xE02B2B
        )
        await context.send(embed=embed)
    elif isinstance(error, commands.BotMissingPermissions):
        embed = discord.Embed(
            title="Error!",
            description="I am missing the permission(s) `" + ", ".join(
                error.missing_permissions) + "` to fully perform this command!",
            color=0xE02B2B
        )
        await context.send(embed=embed)
    elif isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(
            title="Error!",
            # We need to capitalize because the command arguments have no capital letter in the code.
            description=str(error).capitalize(),
            color=0xE02B2B
        )
        await context.send(embed=embed)
    elif isinstance(error, exceptions.UserNotStreamer):
        embed = discord.Embed(
            title="Error!",
            description="You are not a streamer!",
            color=0xE02B2B
        )
        await context.send(embed=embed)
    elif isinstance(error, commands.errors.EmojiNotFound):
        embed = discord.Embed(
            title="Error!",
            description="The emoji you provided is not valid!",
            color=0xE02B2B
        )
        await context.send(embed=embed)
    raise error


async def load_cogs() -> None:
    """
    The code in this function is executed whenever the bot will start.
    """
    for file in os.listdir(f"./cogs"):
        if file.endswith(".py"):
            extension = file[:-3]
            try:
                await bot.load_extension(f"cogs.{extension}")
                print(f"Loaded extension '{extension}'")
            except Exception as e:
                exception = f"{type(e).__name__}: {e}"
                print(f"Failed to load extension {extension}\n{exception}")

async def setup() -> None:
    await init_db()
    await load_cogs()
    print("\n" + "---------Basic Items----------")
    await db_manager.add_basic_items()
    print("\n" + "---------Chests----------")
    await db_manager.add_chests()   
    print("\n" + "---------Shop Items----------")
    await db_manager.add_shop_items()
    print("\n" + "---------Enemies----------")
    await db_manager.add_enemies()
    print("\n" + "---------Quests----------")
    await db_manager.add_quests()
    print("\n" + "---------Quests to Board----------")
    await db_manager.add_quests_to_board()
    print("\n" + "---------Structures----------")
    await db_manager.add_structures()
    print("\n" + "---------COPY PASTE ITEMS----------")
    await db_manager.print_items()
    print("\n" + "-------------------")

@bot.event
async def on_ready() -> None:
    await setup()
    print(f"Logged in as {bot.user.name}")
    print(f"discord.py API version: {discord.__version__}")
    print(f"Python version: {platform.python_version()}")
    print(f"Running on: {platform.system()} {platform.release()} ({os.name})")
    print("-------------------")
    status_task.start()
    if config["sync_commands_globally"]:
        print("Syncing commands globally...")
        await bot.tree.sync()
        print("Done syncing commands globally!")
    print("-------------------")
    #print("Structure Spawn Task Started")
    #structure_spawn_task.start()
    #print("-------------------")
    print("Mob Spawn Task Started")
    mob_spawn_task.start()
    print("-------------------")
    # Run setup function
    # Run twitch bot file
    subprocess.Popen([sys.executable, r'twitch.py'])

bot.run(config["token"])
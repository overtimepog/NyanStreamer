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
import traceback
from typing import Any, Union
import requests
import time

import aiosqlite
import discord
from discord.ext import commands, tasks
from discord.ext.commands import Bot, Context
from discord.ext.commands import Context, has_permissions

from helpers import battle, checks, db_manager, hunt, mine
from assets import endpoints

import exceptions
from helpers import db_manager
#import twitch
#from twitchAPI.twitch import Twitch
#from twitchAPI.types import AuthScope
import lavalink
import aiofiles

cash = "⌬"
if not os.path.isfile("config.json"):
    sys.exit("'config.json' not found! Please add it and try again.")
else:
    with open("config.json") as file:
        config = json.load(file)

#twitch_client_id = config["CLIENT_ID"]
#twitch_client_secret = config["CLIENT_SECRET"]
#twitch = Twitch(twitch_client_id, twitch_client_secret)
#twitch.authenticate_app([])

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

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

"""
Uncomment this if you don't want to use prefix (normal) commands.
It is recommended to use slash commands and therefore not use prefix commands.

If you want to use prefix commands, make sure to also enable the intent below in the Discord developer portal.
"""
intents.message_content = True

bot = Bot(command_prefix=commands.when_mentioned_or(
    config["prefix"]), intents=intents, help_command=None)


async def init_db():
    db = await aiosqlite.connect('database/database.db')
    async with aiofiles.open("database/schema.sql", mode="r", encoding="utf-8") as file:
        script = await file.read()
        await db.executescript(script)
    await db.close()


"""
Create a bot variable to access the config file in cogs so that you don't need to import it every time.

The config is available using the following code:
- bot.config # In this file
- self.bot.config # In cogs
"""
bot.config = config # type: ignore   
    

#every 12 hours the shop will reset, create a task to do this
#every 5 hours a structure will spawn in the channel named "nyanstreamer-structures"
@tasks.loop(minutes=90)
async def structure_spawn_task() -> None:       
    #get the structures channel
    for bot_guild in bot.guilds:
        #if bot_guild.id == 1070882685855211641:
        #    print("Skipping " + bot_guild.name + " because it's the Connections server")
        #    continue
        #reset the guilds current structure
        channel = discord.utils.get(bot_guild.text_channels, topic="Sigma")
        if channel is None:
            #print("A channel with the topic nyanstreamer-structures does not exist in " + bot_guild.name)
            continue
        
        if await db_manager.get_current_structure(bot_guild.id) is not None: # type: ignore
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
        await db_manager.edit_current_structure(bot_guild.id, structureid) # type: ignore

@tasks.loop(minutes=30)
async def mob_spawn_task() -> None:
    mobs = await db_manager.get_all_enemies()
    for bot_guild in bot.guilds:
        #if bot_guild.id == 1070882685855211641:
        #    print("Skipping " + bot_guild.name + " because it's the Connections server")
        #    continue
        #reset the guilds current structure
        channel = discord.utils.get(bot_guild.text_channels, topic="sigma")
        if channel is None:
            #print("A channel with the topic nyanstreamer-structures does not exist in " + bot_guild.name)
            continue
        
        if await db_manager.get_current_structure(bot_guild.id) is not None: # type: ignore
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
    streamers = await db_manager.view_streamers()
    streamer_count = len(streamers)
    #get the server count
    server_count = len(bot.guilds)
    statuses = [f"With {streamer_count} Streamers!", "s.help", 'UwU', f"to {server_count} Servers!"]
    await bot.change_presence(activity=discord.Streaming(name=random.choice(statuses), url="https://www.twitch.tv/overtimepog", twitch_name="overtimepog"))

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


async def update_starboard(reaction: discord.Reaction, user: Union[discord.Member, discord.User], remove: bool = False) -> None:
    config = await db_manager.get_starboard_config(reaction.message.guild.id)
    if not config or not config["is_enabled"]:
        return

    if str(reaction.emoji) == config["star_emoji"]:
        starred_message = await db_manager.get_starred_message_by_id(reaction.message.id)
        if starred_message:
            await db_manager.update_star_count(reaction.message.id, reaction.count if not remove else reaction.count - 1)

            starboard_channel = reaction.message.guild.get_channel(config["starboard_channel_id"])
            if starboard_channel:
                try:
                    starboard_message = await starboard_channel.fetch_message(starred_message["starboard_entry_id"])
                    new_embed = starboard_message.embeds[0]
                    new_embed.title = f"{reaction.emoji} {reaction.count} | Starred Message"
                    await starboard_message.edit(embed=new_embed)
                    
                    if remove and reaction.count < config["star_threshold"]:
                        await starboard_message.delete()
                        await db_manager.remove_starred_message(reaction.message.id)
                except discord.NotFound:
                    await db_manager.remove_starred_message(reaction.message.id)
        else:
            if reaction.count >= config["star_threshold"]:
                message_link = f"https://discord.com/channels/{reaction.message.guild.id}/{reaction.message.channel.id}/{reaction.message.id}"
                direct_links = [url for url in reaction.message.content.split() if url.startswith("https://media.discordapp.net/attachments/")]
                items = direct_links + [attachment.url for attachment in reaction.message.attachments] + [sticker.url for sticker in reaction.message.stickers]

                embed = discord.Embed(
                    title=f"{reaction.emoji} {reaction.count} | Starred Message",
                    description=f"{reaction.message.content}\n\n[Jump to message]({message_link})",
                    color=discord.Color.gold()
                )
                embed.set_author(name=reaction.message.author.display_name, icon_url=reaction.message.author.avatar.url)

                if len(items) == 1:
                    embed.set_image(url=items[0])
                elif len(items) > 1:
                    embed.description += "\n\nAttachments:\n" + "\n".join([f"[Link {i+1}]({url})" for i, url in enumerate(items)])

                starboard_channel = reaction.message.guild.get_channel(config["starboard_channel_id"])
                if starboard_channel:
                    starboard_message = await starboard_channel.send(embed=embed)
                    await db_manager.add_starred_message(
                        message_id=reaction.message.id,
                        guild_id=reaction.message.guild.id,
                        channel_id=reaction.message.channel.id,
                        author_id=reaction.message.author.id,
                        star_count=reaction.count,
                        starboard_entry_id=starboard_message.id,
                        message_link=message_link,
                        message_content=reaction.message.content,
                        attachment_url=items[0] if items else None
                    )

@bot.event
async def on_reaction_add(reaction: discord.Reaction, user: Union[discord.Member, discord.User]) -> None:
    await update_starboard(reaction, user)

@bot.event
async def on_reaction_remove(reaction: discord.Reaction, user: Union[discord.Member, discord.User]) -> None:
    await update_starboard(reaction, user, remove=True)

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
        retry_after = int(error.retry_after)  # Get the retry_after value in seconds
        current_time = int(time.time())  # Get the current time in seconds since the Unix Epoch
        retry_time = current_time + retry_after  # Calculate the Unix timestamp for the retry time

        embed = discord.Embed(
            title="Hey, please slow down!",
            description=f"You can use this command again <t:{retry_time}:R>.",
            color=0xE02B2B
        )
        await context.send(embed=embed, ephemeral=True)
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
        await context.send(embed=embed, ephemeral=True)
    elif isinstance(error, exceptions.UserNotOwner):
        """
        Same as above, just for the @checks.is_owner() check.
        """
        embed = discord.Embed(
            title="Error!",
            description="You are not the owner of the bot!",
            color=0xE02B2B
        )
        await context.send(embed=embed, ephemeral=True)
    elif isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(
            title="Error!",
            description="You are missing the permission(s) `" + ", ".join(
                error.missing_permissions) + "` to execute this command!",
            color=0xE02B2B
        )
        await context.send(embed=embed, ephemeral=True)
    elif isinstance(error, commands.BotMissingPermissions):
        embed = discord.Embed(
            title="Error!",
            description="I am missing the permission(s) `" + ", ".join(
                error.missing_permissions) + "` to fully perform this command!",
            color=0xE02B2B
        )
        await context.send(embed=embed, ephemeral=True)
    elif isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(
            title="Error!",
            # We need to capitalize because the command arguments have no capital letter in the code.
            description=str(error).capitalize(),
            color=0xE02B2B
        )
        await context.send(embed=embed, ephemeral=True)
    elif isinstance(error, exceptions.UserNotStreamer):
        embed = discord.Embed(
            title="Error!",
            description="You are not a streamer!",
            color=0xE02B2B
        )
        await context.send(embed=embed, ephemeral=True)
    elif isinstance(error, commands.errors.EmojiNotFound):
        embed = discord.Embed(
            title="Error!",
            description="The emoji you provided is not valid!",
            color=0xE02B2B
        )
        await context.send(embed=embed, ephemeral=True)
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
                print(f"Failed to load extension {extension}")
                traceback.print_exception(type(e), e, e.__traceback__)

async def setup() -> None:
    print("\n---------Basic Items----------")
    await db_manager.clear_basic_items()
    await db_manager.add_basic_items()
    print("\n---------Shop Items----------")
    await db_manager.clear_shop()
    await db_manager.add_shop_items()
    print("\n---------Chests----------")
    await db_manager.clear_chests()
    await db_manager.add_chests()
    print("\n---------Jobs----------")
    await db_manager.clear_jobs()
    await db_manager.add_jobs_and_minigames()
    await db_manager.add_jobs_to_jobboard()
    print("\n---------COPY PASTE ITEMS----------")
    await db_manager.print_items()
    print("\n---------Inventory Check----------")
    await db_manager.clean_inventory()
    print("\n-----------------------------")
    
    # Remove the joined_channels.json file if it exists
    if os.path.isfile('joined_channels.json'):
        os.remove('joined_channels.json')
    
    total_guilds = len(bot.guilds)

    async def check_server(i, bot_guild, total_guilds):
        total_members = len([member for member in bot_guild.members if not member.bot])
        if total_members > 10000:
            print(f"\nSkipping Server {i}/{total_guilds}: {bot_guild.name} ID: {bot_guild.id} | USERS: {total_members} (more than 10,000 members)")
            return

        print(f"\nStarting check for Server {i}/{total_guilds}: {bot_guild.name} ID: {bot_guild.id} | Total Users: {total_members}")

        start_time = time.time()

        member_counter = 0
        for member in bot_guild.members:
            if member.bot:
                continue
            member_counter += 1
            checkUser = await db_manager.check_user(member.id)
            if checkUser is None:
                await db_manager.get_user(member.id, member.name)

        end_time = time.time()
        duration = end_time - start_time

        print(f"\nFinished check for Server {i}/{total_guilds}: {bot_guild.name} ID: {bot_guild.id} | Total Users: {total_members} | Time taken: {duration:.2f} seconds")

    tasks = [check_server(i, bot_guild, total_guilds) for i, bot_guild in enumerate(bot.guilds, start=1)]
    await asyncio.gather(*tasks)
    print("\nSetup Complete")
    print("\n-----------------------------")

@bot.event
async def on_ready() -> None:
    await init_db()
    await db_manager.create_leaderboard_categories()
    print("\n-----------------------------")
    print(f"Logged in as {bot.user.name}")
    print(f"discord.py API version: {discord.__version__}")
    print(f"Python version: {platform.python_version()}")
    print(f"Running on: {platform.system()} {platform.release()} ({os.name})")
    print("\n---------Loading Cogs----------")
    await setup()
    await load_cogs()
    status_task.start()
    if config["sync_commands_globally"]:
        print("Syncing commands globally...")
        await bot.tree.sync()
        print("Done syncing commands globally!")
    print("\n-----------------------------")
    #print("Structure Spawn Task Started")
    #structure_spawn_task.start()
    #print("-------------------")
    #print("Mob Spawn Task Started")
    #mob_spawn_task.start()
    #print("-------------------")
    # Run setup function
    # Run twitch bot file
    #run the drawing file 
    #subprocess.Popen([sys.executable, r'drawing_code/main.py'])
    #subprocess.Popen([sys.executable, r'twitch.py'])

#when the bot joins a server, add all the members to the database
@bot.event
async def on_guild_join(guild: discord.Guild) -> None:
    print("Joined " + guild.name + " ID: " + str(guild.id))
    for member in guild.members:
        if member.bot:
            continue
        await db_manager.get_user(member.id, member.name)

#when a user joins a server, add them to the database
@bot.event
async def on_member_join(member: discord.Member) -> None:
    if member.bot:
        return
    #if the user is not in the database, add them
    checkUser = await db_manager.check_user(member.id)
    if checkUser == None:
        await db_manager.get_user(member.id, member.name)

bot.run(config["token"])
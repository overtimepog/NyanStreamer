"""
Copyright © Krypton 2022 - https://github.com/kkrypt0nn (https://krypton.ninja)
Description:
This is a template to create your own discord bot in python.

Version: 5.4
"""

import asyncio
import json
import os
import platform
import random
import sys
import subprocess

import aiosqlite
import discord
from discord.ext import commands, tasks
from discord.ext.commands import Bot, Context

import exceptions
from helpers import db_manager, randomEncounter
import twitch

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




@bot.event
async def on_ready() -> None:
    """
    The code in this even is executed when the bot is ready
    """
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


@bot.event
async def on_member_join(member):
    embed = discord.Embed(title="This Sever has DankStreamer!", description="Please read the rules type `accept` to gain access to the bot :).", color=0x00ff00)
    #send a button to the user
    await member.send(embed=embed)
    #look for the word "accept" in the user's message
    def check(m):
        return m.content == "accept" and m.channel == member.dm_channel
    #wait for the user to send the word "accept"
    msg = await bot.wait_for('message', check=check)
    #if the user sends the word "accept", run the code below
    if msg.content == "accept":
        await db_manager.add_user(member.id, False)
        print(f"Added {member} to the database.")
        await member.send("You have been added to the database! You can now use the bot :).")



@tasks.loop(minutes=1.0)
async def status_task() -> None:
    """
    Setup the game status task of the bot
    """
    statuses = ["With Streamers!", "/help", "Sub to Overtime"]
    await bot.change_presence(activity=discord.Game(random.choice(statuses)))


@bot.event
async def on_message(message: discord.Message) -> None:
    """
    The code in this event is executed every time someone sends a message, with or without the prefix

    :param message: The message that was sent.
    """
    #wait for a different message from the webhook
    try:
        if message.guild.id == 1070882685855211641:
            print("Message was sent from the connections Server")
                #wait for the twitch ID
            if message.content.startswith("TWITCH ID: "):
                global twitch_id
                    #remove the TWITCH ID: from the message and then connect the two accounts together
                twitch_id = message.content.replace("TWITCH ID: ", "")
                print(twitch_id)
                #create the boolean variable has_twitch
                has_twitch = True
                has_discord = True
                has_twitch_user = True
                #connect the two accounts
                #if i is more than 2, break the loop

            if message.content.startswith("TWITCH USERNAME: "):
                global twitch_username
                twitch_username = message.content.replace("TWITCH USERNAME: ", "")
                print(twitch_username)
                has_twitch_user = True
                has_twitch = False
                has_discord = True
                #connect the two accounts
                #if i is more than 2, break the loop

            if message.content.startswith("DISCORD ID: "):
                global discord_id
                discord_id = message.content.replace("DISCORD ID: ", "")
                has_discord = True
                has_twitch = False
                #create a global variable to store the discord ID
                print(discord_id)

            #only if both the discord ID and the twitch ID have been found, connect the two accounts
            if has_twitch and has_discord and has_twitch_user:
                await db_manager.connect_twitch_id(discord_id, twitch_id)
                await db_manager.connect_twitch_name(discord_id, twitch_username)
                #send a message to the user saying that the accounts have been connected
                await message.channel.send(f"Connected {discord_id} to {twitch_id}!")
                print(f"Connected {discord_id} to {twitch_id}!")
                #delete the channel
                await message.channel.delete()
    #on AttributeError, the message was not sent from the connections server, so ignore it
    except AttributeError:
        pass
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

asyncio.run(init_db())
asyncio.run(load_cogs())
print("\n" + "---------Basic Items----------")
asyncio.run(db_manager.add_basic_items())
print("\n" + "---------Shop Items----------")
asyncio.run(db_manager.add_shop_items())
print("\n" + "---------Enemies----------")
asyncio.run(db_manager.add_enemies())
print("\n" + "---------Quests----------")
asyncio.run(db_manager.add_quests())
print("\n" + "---------Quests to Board----------")
asyncio.run(db_manager.add_quests_to_board())
print("\n" + "------------------------")
#run twitch bot file
subprocess.Popen([sys.executable, r'twitch.py'])
bot.run(config["token"])
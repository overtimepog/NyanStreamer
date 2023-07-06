import os
import re # for importing env vars for the bot to use
from twitchio.ext import commands
import asyncio
import json
import os
import platform
import random
import sys

import aiosqlite
import aiohttp
from helpers import db_manager
from startTwis import main

if not os.path.isfile("config.json"):
    sys.exit("'config.json' not found! Please add it and try again.")
else:
    with open("config.json") as file:
        config = json.load(file)

class TwitchBot(commands.Bot):

    def __init__(self):
        # Initialise our Bot with our access token, prefix and a list of channels to join on boot...
        super().__init__(token=config["TOKEN"], prefix='nya ', initial_channels=[config["CHANNEL"]])

    async def event_ready(self):
        # We are logged in and ready to chat and use commands...
        print(f'Logged in as | {self.nick}')
        print(f'User id is | {self.user_id}')
        join_message = f"Hello! I'm NyanStreamer and I'm here to help you with your adventure! Type !help for a list of commands."
        self.join_message = join_message
        #check if new streamers have been added to the database
        while True:
            streamerList = await db_manager.view_streamers()
            channels = []
            joined_channels = []
            # If the JSON file already exists, read it
            if os.path.isfile('joined_channels.json'):
                with open('joined_channels.json', 'r') as f:
                    joined_channels = json.load(f)
    
            for i in streamerList:
                streamer_channel = i[1]
                def remove_prefix(text, prefix):
                    if text.startswith(prefix):
                        return text[len(prefix):]
                    return text
                streamer_channel_name = remove_prefix(streamer_channel, "https://www.twitch.tv/")
                # Skip joining if already joined
                if streamer_channel_name not in joined_channels:
                    #add each channel a list of channels to join
                    channels.append(streamer_channel_name)
                    print(f"Joining {streamer_channel_name}...")
            try:
                await TwitchBot.join_channels(self, channels)
                # Add the newly joined channels to our list of joined channels
                joined_channels.extend(channels)
            except KeyError or asyncio.exceptions.CancelledError:
                pass
            if len(channels) == 0:
                pass
            else:
                print(f"Joined {len(channels)} channels.")
                # Save the joined channels to the JSON file
                with open('joined_channels.json', 'w') as f:
                    json.dump(joined_channels, f)
                #setup twis from here
                #print whats happening
                print("Setting up Twis...")
                main()
            await asyncio.sleep(600)
    
    #when command on cooldown
    async def event_command_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"This command is on cooldown, please retry in {error.retry_after:.2f}s.")

    @commands.command()
    async def hello(self, ctx: commands.Context):
        # Send a hello back!
        await ctx.send(f'Hello {ctx.author.name}!')

    @commands.command()
    async def help(self, ctx: commands.Context):
        #send a help message with all the commands
        await ctx.send("nya drop: Drops a random item from your channel to a random viewer in chat\n")

    #command to drop an item to a random viewer in chat, get the random veiwer from https://tmi.twitch.tv/group/user/{channel}/chatters and then send a message to them
    @commands.cooldown(rate=1, per=60, bucket=commands.Bucket.channel)
    @commands.command()
    async def drop(self, ctx: commands.Context):
        if ctx.author.is_mod:
            channel = TwitchBot.get_channel(self, ctx.channel.name)
            chatters = channel.chatters
            names = [chatter.name for chatter in chatters]
            itemGiven = False  # Introduce a boolean flag
            for _ in range(len(names)):  # Change from infinite loop to finite loop over chatters
                randomViewer = random.choice(names)
                userTwitchID = await db_manager.get_twitch_id_of_channel(randomViewer)
                isConnected = await db_manager.is_twitch_connected(userTwitchID)
                if isConnected:
                    userDiscordID = await db_manager.get_user_id(userTwitchID)
                    items = await db_manager.get_all_streamer_items(channel.name)

                    if len(items) == 0:
                        print("no items for channel: " + ctx.channel.name)
                        await ctx.send(f"There are no items to drop in {ctx.channel.name}, giving money instead :)!")
                        money = random.randint(200, 5000)
                        await db_manager.add_money(userDiscordID, money)
                        await ctx.send(f"{randomViewer} has been given {money} coins by {ctx.author.name}!")
                        itemGiven = True
                        break

                    randomItem = random.choice(items)

                    prefix = randomItem[0]
                    channel = randomItem[1]
                    itemID = randomItem[2]
                    itemName = randomItem[3]

                    print(prefix)
                    print(channel)
                    print(itemID)
                    print(itemName)
                    print(randomViewer)
                    itemgiven = await db_manager.add_streamer_item_to_user(userDiscordID, itemID)
                    if itemgiven == 0:
                        await ctx.send(f"{randomViewer} already has {itemName} in their inventory!, they have been given 1000 coins instead!")
                        await db_manager.add_money(userDiscordID, 1000)
                        itemGiven = True
                        break
                    elif itemgiven == 1:
                        await ctx.send(f"{randomViewer} has been given {itemName} by {ctx.author.name}!")
                        itemGiven = True
                        break
            if not itemGiven:  # If the loop ended and no items were given
                await ctx.send("No viewer has been given an item.")
        else:
            await ctx.send(f"You do not have permission to use this command!")
        
if __name__ == "__main__":
    bot = TwitchBot()
    bot.run()
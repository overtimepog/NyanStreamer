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

if not os.path.isfile("config.json"):
    sys.exit("'config.json' not found! Please add it and try again.")
else:
    with open("config.json") as file:
        config = json.load(file)

class TwitchBot(commands.Bot):

    def __init__(self):
        # Initialise our Bot with our access token, prefix and a list of channels to join on boot...
        super().__init__(token=config["TOKEN"], prefix='d.', initial_channels=[config["CHANNEL"]])

    async def event_ready(self):
        # We are logged in and ready to chat and use commands...
        print(f'Logged in as | {self.nick}')
        print(f'User id is | {self.user_id}')
        join_message = f"Hello! I'm DankStreamer and I'm here to help you with your adventure! Type !help for a list of commands."
        self.join_message = join_message
        #check if new streamers have been added to the database
        while True:
            streamerList = await db_manager.view_streamers()
            channels = []
            for i in streamerList:
                streamer_channel = i[1]
                def remove_prefix(text, prefix):
                    if text.startswith(prefix):
                        return text[len(prefix):]
                    return text
                streamer_channel_name = remove_prefix(streamer_channel, "https://www.twitch.tv/")
                #add each channel a list of channels to join
                channels.append(streamer_channel_name)
                print(f"Joining {streamer_channel_name}...")
            await TwitchBot.join_channels(self, channels)
            print(f"Joined {len(channels)} channels.")
            await asyncio.sleep(600)

    @commands.command()
    async def hello(self, ctx: commands.Context):
        # Send a hello back!
        await ctx.send(f'Hello {ctx.author.name}!')

    #command to drop an item to a random viewer in chat, get the random veiwer from https://tmi.twitch.tv/group/user/{channel}/chatters and then send a message to them
    @commands.cooldown(rate=1, per=120, bucket=commands.BucketType.channel)
    @commands.command()
    async def drop(self, ctx: commands.Context):
        if ctx.author.is_mod:
            channel = TwitchBot.get_channel(self, ctx.channel.name)
            chatters = channel.chatters
            names = [chatter.name for chatter in chatters]

            while True:
                randomViewer = random.choice(names)
                userTwitchID = await db_manager.get_twitch_id_of_channel(randomViewer)
                isConnected = await db_manager.is_twitch_connected(userTwitchID)
                if isConnected:
                    userDiscordID = await db_manager.get_user_id(userTwitchID)
                    items = await db_manager.get_all_streamer_items(channel.name)

                    if len(items) == 0:
                        print("no items for channel: " + ctx.channel.name)
                        await ctx.send(f"There are no items to drop in {ctx.channel.name}, giving money instead :)!")
                        money = random.randint(25, 1000)
                        await db_manager.add_money(userDiscordID, money)
                        await ctx.send(f"{randomViewer} has been given {money} coins by {ctx.author.name}!")
                        return

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
                        await ctx.send(f"{randomViewer} already has {itemName} in their inventory!, you have been given 1000 coins instead!")
                        await db_manager.add_money(userDiscordID, 1000)
                        return
                    elif itemgiven == 1:
                        await ctx.send(f"{randomViewer} has been given {itemName} by {ctx.author.name}!")
                        return

                    money = random.randint(25, 1000)
                    await db_manager.add_money(userDiscordID, money)
                    await ctx.send(f"{randomViewer} has been given {money} coins by {ctx.author.name}!")
                    return
                else:
                    await ctx.send(f"{randomViewer} is not connected to discord! ReRolling...")
        else:
            await ctx.send(f"You do not have permission to use this command!")
        
        
if __name__ == "__main__":
    bot = TwitchBot()
    bot.run()
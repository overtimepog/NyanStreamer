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
    @commands.cooldown(rate=1, per=120, bucket=commands.Bucket.channel)
    @commands.command()
    #add a cooldown of 1 hour
    async def drop(self, ctx: commands.Context):
        #make sure only mods of the channel can use this command
        if ctx.author.is_mod:
            #get the viewers from the channel
            channel = TwitchBot.get_channel(self, ctx.channel.name)
            chatters = channel.chatters
            names = [chatter.name for chatter in chatters]
            randomViewer = random.choice(names)
            print(randomViewer)
            channelName = channel.name
            channelName = str(channelName)
            print(channelName)
            channelName = str(channelName)
            #add the vips to the viewers list
            #get a random viewer from the list
            #get the item from the database
            items = await db_manager.get_all_streamer_items(channelName)
            userTwitchID = await db_manager.get_twitch_id_of_channel(randomViewer)
            isConnected = await db_manager.is_twitch_connected(userTwitchID)
            if isConnected == True:
                #get the discord id of the random user
                userDiscordID = await db_manager.get_user_id(userTwitchID)
                if len(items) == 0:
                    #send a message to the channel saying there are no items to drop
                    print("no items for channel: " + ctx.channel.name)
                    await ctx.send(f"There are no items to drop in {ctx.channel.name}, giving money instead :)!")
                    #drop a random basic item instead
                    #get a random item from the list
                    
                    money = random.randint(25, 1000)
                    await db_manager.add_money(userDiscordID, money)
                    await ctx.send(f"{randomViewer} has been given {money} coins by {ctx.author.name}!")
                    return

                #get a random item from the list
                randomItem = random.choice(items)
                    #`streamer_prefix` varchar(20) NOT NULL,
                    #`item_id` varchar(20) NOT NULL,
                    #`item_name` varchar NOT NULL,
                    #`item_price` varchar(255) NOT NULL,
                    #`item_emoji` varchar(255) NOT NULL,
                    #`item_rarity` varchar(255) NOT NULL,
                    #`twitch_id` varchar(255) NOT NULL,
                    #`item_type` varchar(255) NOT NULL,
                    #`item_damage` int(11) NOT NULL,
                    #`item_element` varchar(255) NOT NULL,
                    #`item_crit_chance` int(11) NOT NULL,
                    #`item_effect` varchar(255) NOT NULL,
                    #`isUsable` boolean NOT NULL,
                    #`isEquippable` boolean NOT NULL
                #CREATE TABLE IF NOT EXISTS `streamer_items` (
                #  `streamer_prefix` varchar(20) NOT NULL,
                #  `channel` varchar(20) NOT NULL,
                #  `item_id` varchar(20) NOT NULL,
                #  `item_name` varchar NOT NULL,
                #  `item_emoji` varchar(255) NOT NULL,
                #  `item_rarity` varchar(255) NOT NULL
                #);

                prefix = randomItem[0]
                channel = randomItem[1]
                itemID = randomItem[2]
                itemName = randomItem[3]

                #print all of it
                print(prefix)
                print(channel)
                print(itemID)
                print(itemName)
                print(randomViewer)

                #get all the data from the item

                #make sure the random user is connected to discord
                #get the twitch id of the random user
                    #get the discord name of the random user
                    #send a message to the random user
                    #add the item to the users inventory
                    #give it a 50% chance for the item to be dropped, and the other 75% it will give random amount of money
                chance = random.randint(1, 4)
                if chance <= 2:
                    itemgiven = await db_manager.add_streamer_item_to_user(userDiscordID, itemID)
                    #send a message to the random user saying they have been given an item
                    if itemgiven == 0:
                        await ctx.send(f"{randomViewer} already has {itemName} in their inventory!, you have been given 5000 coins instead!")
                        await db_manager.add_money(userDiscordID, 5000)
                        return
                    elif itemgiven == 1:
                        await ctx.send(f"{randomViewer} has been given {itemName} by {ctx.author.name}!")
                        return
                    #get a random amount of money
                money = random.randint(25, 1000)
                await db_manager.add_money(userDiscordID, money)
                await ctx.send(f"{randomViewer} has been given {money} coins by {ctx.author.name}!")
                return
            else:
                await ctx.send(f"{randomViewer} is not connected to discord!, please connect to discord to receive items from drops!, ReRolling...")
                await TwitchBot.drop(self, ctx)
        else:
            await ctx.send(f"You do not have permission to use this command!")
        
        
if __name__ == "__main__":
    bot = TwitchBot()
    bot.run()
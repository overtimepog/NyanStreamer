import os # for importing env vars for the bot to use
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
    @commands.cooldown(rate=1, per=1800, bucket=commands.Bucket.channel)
    @commands.command()
    #add a cooldown of 1 hour
    async def drop(self, ctx: commands.Context):
        #make sure only mods of the channel can use this command
        if ctx.author.is_mod:
            #get the viewers from the channel
            channel = TwitchBot.get_channel(self, ctx.channel.name)
            channelName = channel.name
            channelName = str(channelName)
            twitchID = await db_manager.get_twitch_id_of_channel(channelName)
            print(channelName)
            channelName = str(channelName)
            #send a request to the twitch api to get the viewers
            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://tmi.twitch.tv/group/user/{channelName}/chatters") as resp:
                    text = await resp.text()
                    print(text)
                    try:
                        data = json.loads(text)
                    except json.JSONDecodeError:
                        print("Failed to decode json from response")
                        data = None
            #get the viewers from the json
            viewers = data["chatters"]["viewers"]
            vips = data["chatters"]["vips"]
            list = viewers + vips
            #add the vips to the viewers list
            #get a random viewer from the list
            randomViewer = random.choice(list)
            #get the item from the database
            items = await db_manager.get_all_streamer_items(twitchID)
            basic_items = db_manager.get_all_basic_items()
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


                #get all the data from the item
                prefix = randomItem[0]
                itemID = randomItem[1]
                itemName = randomItem[2]
                itemPrice = randomItem[3]
                itemEmoji = randomItem[4]
                itemRarity = randomItem[5]
                twitchID = randomItem[6]
                itemType = randomItem[7]
                itemDamage = randomItem[8]
                itemSubType = randomItem[9]
                itemCritChance = randomItem[10]
                itemEffect = randomItem[11]
                isUsable = randomItem[12]
                isEquippable = randomItem[13]
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
                        await ctx.send(f"{randomViewer} already has {randomItem[2]} in their inventory!, you have been given 5000 coins instead!")
                        await db_manager.add_money(userDiscordID, 5000)
                        return
                    elif itemgiven == 1:
                        await ctx.send(f"{randomViewer} has been given {randomItem[2]} by {ctx.author.name}!")
                        return
                    #get a random amount of money
                money = random.randint(25, 1000)
                await db_manager.add_money(userDiscordID, money)
                await ctx.send(f"{randomViewer} has been given {money} coins by {ctx.author.name}!")
                return
            else:
                await print(f"{randomViewer} is not connected to discord!, please connect to discord to receive items from drops!, ReRolling...")
                await self.drop(ctx)
        else:
            await ctx.send(f"You do not have permission to use this command!")
        
        
if __name__ == "__main__":
    bot = TwitchBot()
    bot.run()
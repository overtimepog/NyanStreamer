import os # for importing env vars for the bot to use
from twitchio.ext import commands
import asyncio
import json
import os
import platform
import random
import sys

import aiosqlite

from helpers import db_manager, randomEncounter

if not os.path.isfile("config.json"):
    sys.exit("'config.json' not found! Please add it and try again.")
else:
    with open("config.json") as file:
        config = json.load(file)

class TwitchBot(commands.Bot):

    def __init__(self):
        # Initialise our Bot with our access token, prefix and a list of channels to join on boot...
        super().__init__(token=config["TOKEN"], prefix='/', initial_channels=[config["CHANNEL"]])

    async def event_ready(self):
        # We are logged in and ready to chat and use commands...
        print(f'Logged in as | {self.nick}')
        print(f'User id is | {self.user_id}')
        join_message = f"Hello! I'm DankStreamer and I'm here to help you with your adventure! Type /help for a list of commands."
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
            await asyncio.sleep(300)

    @commands.command()
    async def hello(self, ctx: commands.Context):
        # Send a hello back!
        await ctx.send(f'Hello {ctx.author.name}!')
        
if __name__ == "__main__":
    bot = TwitchBot()
    bot.run()
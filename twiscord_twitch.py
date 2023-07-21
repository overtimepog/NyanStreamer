import os
import json
import random
import asyncio
from twitchio.ext import commands as twitch_commands
from helpers import db_manager

class TwiscordTwitch(twitch_commands.Bot):
    def __init__(self):
        with open("config.json") as file:
            config = json.load(file)

        token = config['TOKEN']
        irc_token = config['TMI_TOKEN']
        self.client_id = config['CLIENT_ID']
        nick = config['BOT_NICK'].lower()
        self.prefix = config['BOT_PREFIX']


        # Load joined channels from JSON file
        try:
            with open('joined_channels.json', 'r') as f:
                self.initial_channels = json.load(f)
        except FileNotFoundError:
            self.initial_channels = []

        super().__init__(token=token, irc_token=irc_token, client_id=self.client_id, nick=nick, prefix=self.prefix, initial_channels=self.initial_channels)

    async def event_ready(self):
        #print(f"Twitch Ready | {self.nick}")
        self._is_ready_ = True
        for channel in self.initial_channels:
            self.channel = self.get_channel(channel)
            print(f"Twiscord Enabled for Twitch Channel | {self.channel.name}")
        if self.discord_bot._is_ready_:
            #content = "[Twiscord] Both bots are set up."
            ##await self.channel.send(content)
            ##await self.discord_bot.channel.send(content)
            #print(content)
            pass
 
    async def event_message(self, message):
        if message.author is None or message.author.name == self.nick.lower():
            return

        if not self.discord_bot._is_ready_:
            print("[Twiscord] Discord not initialized.")
            #await message.channel.send("[Twiscord] Discord not initialized.")
            return

        sender_name = message.author.display_name if message.author.display_name else message.author.name

        role = None
        if message.author.name in self.initial_channels:
            role = "Streamer"
        elif message.author.is_mod:
            role = "Moderator"
        elif message.author.is_vip:
            role = "VIP"
        elif message.author.is_subscriber:
            role = "Subscriber"

        content = f"{'**' + role + '** ' if role else ''}{sender_name} » {message.content}"
        #if the content contains @everyone or @here, replace it with @ everyone or @ here
        if "@everyone" in content:
            content = content.replace("@everyone", "@ everyone")
        if "@here" in content:
            content = content.replace("@here", "@ here")
        print(f"[twitch ] {content}")

        if message.content.startswith(self.prefix):
            await self.handle_commands(message)
        else:
            #get the channel name its sending to
            channel_name = message.channel.name
            #get the discord channel id from the database
            discord_channel_id = await db_manager.get_discord_channel_id_chat(channel_name)
            #print(f"discord_channel_id: {discord_channel_id}")
            try:
                discord_channel_id = int(discord_channel_id)
                #get the discord channel object from the id
                discord_channel = self.discord_bot.get_channel(discord_channel_id)
                #print(f"discord_channel: {discord_channel}")
                #send the message to the discord channel
                await discord_channel.send(content)
            except ValueError or TypeError:
                return

    @twitch_commands.command(name="discord")
    async def discord(self, ctx):
        await ctx.send(self.discord_bot.invite_link)

if __name__ == "__main__":
    print("Sorry, this isn't the file you meant to run.")
    print("You need to run for Twiscord to work ./main.py")

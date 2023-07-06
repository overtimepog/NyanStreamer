import os
import json
import random
import asyncio
from twitchio.ext import commands as twitch_commands

class TwitchBot(twitch_commands.Bot):
    def __init__(self):
        with open("config.json") as file:
            config = json.load(file)

        token = config['TOKEN']
        irc_token = config['TMI_TOKEN']
        self.client_id = config['CLIENT_ID']
        nick = config['BOT_NICK'].lower()
        self.prefix = config['BOT_PREFIX']


        # Load joined channels from JSON file
        with open('joined_channels.json', 'r') as f:
            self.initial_channels = json.load(f)

        super().__init__(token=token, irc_token=irc_token, client_id=self.client_id, nick=nick, prefix=self.prefix, initial_channels=self.initial_channels)

    async def event_ready(self):
        print(f"Twitch Ready | {self.nick}")
        self._is_ready_ = True
        self.channel = self.get_channel(self.initial_channel)
        if self.discord_bot._is_ready_:
            content = "[Twiscord] Discord and Twitch bots are set up."
            #await self.channel.send(content)
            #await self.discord_bot.channel.send(content)
            print(content)

    async def event_message(self, message):
        if message.author.name == self.nick.lower():
            return

        if not self.discord_bot._is_ready_:
            print("[Twiscord] Discord not initialized.")
            #await message.channel.send("[Twiscord] Discord not initialized.")
            return

        sender_name = message.author.tags['display-name'] if 'display-name' in message.author.tags.keys() else message.author.name

        role = None
        if message.author.name == self.initial_channel:
            role = "Streamer"
        elif message.author.is_mod:
            role = "Moderator"
        elif message.author.is_subscriber:
            role = "Subscriber"

        content = f"{'**' + role + '** ' if role else ''}{sender_name} » {message.content}"
        print(f"[twitch ] {content}")

        if message.content.startswith(self.prefix):
            await self.handle_commands(message)
        else:
            await self.discord_bot.channel.send(content)

    @twitch_commands.command(name="discord")
    async def discord(self, ctx):
        await ctx.send(self.discord_bot.invite_link)

if __name__ == "__main__":
    print("Sorry, this isn't the file you meant to run.")
    print("You need to run for Twiscord to work ./main.py")

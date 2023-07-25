from __future__ import annotations
import json

import time

start_time = time.time()

import asyncio
import datetime
import logging
import os
import sys
from functools import cached_property
from typing import Any, Union

import aiohttp
import discord
import gists
from discord.ext import commands
import pandas as pd
from discord import app_commands

from helpers.context import CustomContext
from cogs.Draw.utils.colour import Colour
from cogs.Draw.draw import DrawView
from cogs.Draw.utils.emoji_cache import EmojiCache
from helpers.constants import LOG_BORDER, NL
from helpers.keep_alive import keep_alive

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

if not os.path.isfile("config.json"):
    sys.exit("'config.json' not found! Please add it and try again.")
else:
    with open("config.json") as file:
        config = json.load(file)

class Bot(commands.Bot):
    COGS = {
        "draw": "Draw.draw",
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.start_time: float
        self.emoji_cache: EmojiCache = EmojiCache(bot=self)

        self.lock = asyncio.Lock()

    @cached_property
    def invite_url(self) -> str:
        perms = discord.Permissions.none()
        perms.send_messages = True
        perms.read_messages = True
        perms.read_message_history = True
        perms.add_reactions = True
        perms.external_emojis = True
        perms.external_stickers = True
        perms.manage_channels = True
        perms.manage_messages = True
        perms.manage_emojis = True
        perms.attach_files = True
        perms.embed_links = True
        return discord.utils.oauth_url(self.user.id, permissions=perms)

    async def get_context(self, message, *, cls=None):
        return await super().get_context(message, cls=cls or CustomContext)

    async def setup_hook(self):
        self.EMOJI_SERVER_IDS = [
            # 1095209373627846706,
            # 1095209373627846706,
            # 1095209396675559557,
            # 1095209424454418522,
            # 1095209448810749974,
            # 1095211521136656457,
            # 1095211546025656340,
            # 1095211570264559696,
            # 1095211594289528884,
            # 1095212928959004694,
            1124233463843795014,
        ]
        self.EMOJI_SERVERS = [
            await self.fetch_guild(_id) for _id in self.EMOJI_SERVER_IDS
        ]

        ext_start = time.time()
        log.info("Started loading extensions" + NL + LOG_BORDER)
        for filename in set(self.COGS.values()):
            start = time.time()
            await self.load_extension(f"cogs.{filename}")
            log.info(
                f"Loaded \033[34;1mcogs.{filename}\033[0m in \033[33;1m{round(time.time()-start, 2)}s\033[0m"
            )
        log.info(
            f"Loaded all extensions in \033[33;1m{round(time.time()-ext_start, 2)}s\033[0m"
            + NL
            + LOG_BORDER
        )

        for name, cog in self.cogs.items():
            try:
                await cog.setup()
            except AttributeError:
                continue

        #sync slash commands
        print("Syncing Slash commands....")
        all_commands = await bot.tree._get_all_commands()
        for command in all_commands:
            await bot.tree.add_command(command)
            print(f"Added {command.name} to Slash commands")
        await bot.tree.sync()
        print("Synced Slash commands")

        time_taken = time.time() - self.start_time
        m, s = divmod(time_taken, 60)
        msg = f"\033[32;1m{self.user}\033[0;32m connected in \033[33;1m{round(m)}m{round(s)}s\033[0;32m.\033[0m"
        print(msg)

    class Embed(discord.Embed):
        COLOUR = 0x9BFFD6

        def __init__(self, **kwargs):
            if kwargs.get("color", None) is None:
                kwargs["color"] = self.COLOUR
            super().__init__(**kwargs)

        def add_field(self, *, name: Any, value: Any, inline: bool = False):
            """Adds a field to the embed object.

            This function returns the class instance to allow for fluent-style
            chaining. Can only be up to 25 fields.

            Parameters
            -----------
            name: :class:`str`
                The name of the field. Can only be up to 256 characters.
            value: :class:`str`
                The value of the field. Can only be up to 1024 characters.
            inline: :class:`bool`
                Whether the field should be displayed inline.
            """

            field = {
                "inline": inline,
                "name": str(name),
                "value": str(value),
            }

            try:
                self._fields.append(field)
            except AttributeError:
                self._fields = [field]

            return self

    async def upload_emoji(
        self, colour: Colour, *, draw_view: DrawView, interaction: discord.Interaction
    ) -> Union[discord.Emoji, discord.PartialEmoji]:
        # First look if there is cache of the emoji
        if (emoji := self.emoji_cache.get_emoji(colour.hex)) is not None:
            return emoji

        async with draw_view.disable(interaction=interaction):
            # Look if emoji already exists in a server
            guild_emoji_lists = []
            for guild in self.EMOJI_SERVERS:
                guild_emojis = await guild.fetch_emojis()
                guild_emoji_lists.append(guild_emojis)
                for guild_emoji in guild_emojis:
                    if colour.hex == guild_emoji.name:
                        self.emoji_cache.add_emoji(guild_emoji)
                        return guild_emoji

            # Emoji does not exist already, proceed to create
            for guild in self.EMOJI_SERVERS:
                try:
                    emoji = await colour.to_emoji(guild)
                except discord.HTTPException:
                    continue
                else:
                    self.emoji_cache.add_emoji(emoji)
                    return emoji
            # If it exits without returning aka there was no space available
            else:
                emoji_to_delete = guild_emoji_lists[0][
                    0
                ]  # Get first emoji from the first emoji server
                await emoji_to_delete.delete()  # Delete the emoji to make space for the new one
                self.emoji_cache.remove_emoji(
                    emoji_to_delete
                )  # Delete that emoji from cache if it exists
                return await self.upload_emoji(
                    colour, draw_view=draw_view, interaction=interaction
                )  # Run again


#get the token from the .json config file
TOKEN = config.get("token")

if __name__ == "__main__":
    bot = Bot(
        command_prefix="nya ",
        owner_ids=[267550284979503104, 761944238887272481],
        case_insensitive=True,
        intents=discord.Intents.all(),
    )
    bot.start_time = start_time
    if os.getenv("REPL_ID") is not None:
        keep_alive()
        try:
            bot.tree.sync()
            print("Synced Slash command for Drawing Code")
            bot.run(TOKEN)
        except discord.HTTPException as error:
            if error.response.status == 429:
                print("\033[0;31mRate-limit detected, restarting process.\033[0m")
                os.system(f"kill 1 && source run")
    else:
        bot.run(TOKEN)

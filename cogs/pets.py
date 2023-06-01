import asyncio
import datetime
import json
import random
import re
import requests
from discord import Webhook, SyncWebhook
import aiohttp
import discord
from discord import Embed, app_commands
from discord.ext import commands
from discord.ext.commands import Context, has_permissions

from helpers import battle, checks, db_manager, hunt, mine
from typing import List, Tuple
from discord.ext.commands.errors import CommandInvokeError


cash = "<:cash:1077573941515792384>"
rarity_colors = {
    "Common": 0x808080,  # Grey
    "Uncommon": 0x319236,  # Green
    "Rare": 0x4c51f7,  # Blue
    "Epic": 0x9d4dbb,  # Purple
    "Legendary": 0xf3af19,  # Gold
    # Add more rarities and colors as needed
}
# Here we name the cog and create a new class for the cog.
class Pets(commands.Cog, name="pets"):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_group(invoke_without_command=True)
    async def pet(self, ctx):
        """The parent pet command."""
        await ctx.send('This is the parent pet command. Use `d.help pet` for more options.')

    @pet.command()
    async def feed(self, ctx):
        """Feed your pet."""
        await ctx.send('You fed your pet!')

    @pet.command()
    async def name(self, ctx, name: str):
        """Name your pet."""
        await ctx.send(f'You named your pet {name}!')

    @pet.command()
    @commands.is_owner()
    async def level(self, ctx):
        """Shows the level of your pet. Only for bot owner."""
        await ctx.send('Your pet is at level 1.')
    
    # You can add more pet-related commands here

def setup(bot):
    bot.add_cog(Pets(bot))
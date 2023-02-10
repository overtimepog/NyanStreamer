
import asyncio
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

from helpers import battle, checks, db_manager, randomEncounter, start, use, games


# Here we name the cog and create a new class for the cog.
class Games(commands.Cog, name="games"):
    def __init__(self, bot):
        self.bot = bot

    # Here we create a new command called "slots".
    @commands.hybrid_command(
        name="slots",
        description="Play a game of slots.",
    )
    async def slots(self, ctx: Context, gamble: int):
        await games.slots(ctx, ctx.author, gamble)



async def setup(bot):
    await bot.add_cog(Games(bot))
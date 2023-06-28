""""
Copyright © Krypton 2022 - https://github.com/kkrypt0nn (https://krypton.ninja)
Description:
This is a template to create your own discord bot in python.

Version: 5.4
"""

import platform
import random

import aiohttp
import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context
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
from helpers import db_manager, bank

from helpers import checks

cash = "⚙"
class Bank(commands.Cog, name="bank"):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="networth",
        description="Shows the networth of a user.",
        usage="networth [user]",
        aliases=["nw", "net"],
    )
    async def networth(self, ctx: Context, user: discord.User = None):
        if user is None:
            user = ctx.author
        await bank.get_and_send_net_worth_embed(ctx, user)

async def setup(bot):
    await bot.add_cog(Bank(bot))

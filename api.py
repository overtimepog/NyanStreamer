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
from helpers import db_manager
from helpers import checks
import math

class API(commands.Cog, name="api"):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_group(
        name="api",
        description="API commands",
    )
    async def api(self, ctx: Context):
        if ctx.invoked_subcommand is None:
            #send an embed with the job commands
            await ctx.send_help(ctx.command)
            return

    @api.command(
        name="claim",
        description="Claim an api key",
    )
    async def claim(self, ctx: commands.Context):
        # Check if the command is run in the server 1113596780408475818
        if ctx.guild.id != 1113596780408475818:
            embed = discord.Embed(
                title="Server Restriction",
                description="This command can only be run in a specific server. Please join [this server](https://discord.com/invite/dMczvnPmAa) and run the command there.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        # Check if the user has the role 1139617118342615082
        if 1139617118342615082 not in [role.id for role in ctx.author.roles]:
            embed = discord.Embed(
                title="Role Requirement",
                description="You must have a specific role to claim an API key. Please support us on [Patreon](https://www.patreon.com/NyanStreamer) to get access.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        # Get the user's API key
        api_key = await db_manager.get_api_key(ctx.author.id)

        if api_key is None:
            # Generate a new API key
            api_key = await db_manager.generate_api_key(ctx.author.id)
            embed = discord.Embed(
                title="API Key Generated",
                description=f"Your new API key is: `{api_key}`",
                color=discord.Color.green()
            )
            try:
                await ctx.author.send(embed=embed)
                await ctx.send("your api key has been sent to your dms")
            except discord.Forbidden:
                await ctx.send("I couldn't send you a DM. Please enable DMs from server members and try again.")
        else:
            # DM the user their existing API key
            embed = discord.Embed(
                title="Your API Key",
                description=f"Your API key is: `{api_key}`",
                color=discord.Color.blue()
            )
            try:
                await ctx.author.send(embed=embed)
                await ctx.send("your api key has been sent to your dms")
            except discord.Forbidden:
                await ctx.send("I couldn't send you a DM. Please enable DMs from server members and try again.")

    @api.command(
        name="revoke",
        description="Revoke a users api key",
    )
    @checks.is_owner()
    async def revoke(self, ctx: commands.Context, user: discord.User):
        # Revoke the user's API key
        await db_manager.revoke_api_key(user.id)
        embed = discord.Embed(
            title="API Key Revoked",
            description=f"{user.mention}'s API key has been revoked.",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)





async def setup(bot):
    await bot.add_cog(API(bot))


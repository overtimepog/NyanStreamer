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

    #withdraw command
    @commands.hybrid_command(
        name="withdraw",
        description="Withdraws money from your bank.",
        usage="withdraw [amount]",
        aliases=["with"],
    )
    async def withdraw(self, ctx: Context, amount: int):
        if amount <= 0:
            await ctx.send("You can't withdraw negative or zero money!")
            return

        # get the user's bank balance
        bank_balance = await db_manager.get_bank_balance(ctx.author.id)
        bank_balance = str(bank_balance)
        # remove the ( and ) and , from the bank balance
        bank_balance = bank_balance.replace("(", "")
        bank_balance = bank_balance.replace(")", "")
        bank_balance = bank_balance.replace(",", "")
        bank_balance = int(bank_balance)
        # check if the user has enough money in their bank
        if bank_balance < amount:
            await ctx.send("You don't have enough money in your bank to withdraw that much!")
            return

        # if the user has enough money in their bank, withdraw the money
        await db_manager.remove_from_bank(ctx.author.id, amount)
        await db_manager.add_money(ctx.author.id, amount)

        # Get the updated balances
        updated_bank_balance = await db_manager.get_bank_balance(ctx.author.id)
        updated_wallet_balance = await db_manager.get_money(ctx.author.id)

        # Create and send the embed with all the information
        embed = Embed(
            title="Withdrawal Successful", 
            description=f"You have successfully withdrawn {amount:,} from your bank.", 
            )
        embed.add_field(name="Withdrawn Amount", value=f"{amount:,}", inline=False)
        embed.add_field(name="Updated Bank Balance", value=f"{updated_bank_balance:,}", inline=False)
        embed.add_field(name="Updated Wallet Balance", value=f"{updated_wallet_balance:,}", inline=False)
        embed.set_footer(text=f"{ctx.author.name}'s updated balances")

        await ctx.send(embed=embed)
        
async def setup(bot):
    await bot.add_cog(Bank(bot))

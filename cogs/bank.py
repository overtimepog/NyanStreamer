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

cash = "⌬"
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

        bank_capacity = await db_manager.get_bank_capacity(ctx.author.id)
        bank_capacity = str(bank_capacity)
        bank_capacity = bank_capacity.replace("(", "")
        bank_capacity = bank_capacity.replace(")", "")
        bank_capacity = bank_capacity.replace(",", "")
        bank_capacity = int(bank_capacity)
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
        #remove the ( and ) and , from the updated balances
        updated_bank_balance = str(updated_bank_balance)
        updated_bank_balance = updated_bank_balance.replace("(", "")
        updated_bank_balance = updated_bank_balance.replace(")", "")
        updated_bank_balance = updated_bank_balance.replace(",", "")
        updated_bank_balance = int(updated_bank_balance)
        
        updated_wallet_balance = str(updated_wallet_balance)
        updated_wallet_balance = updated_wallet_balance.replace("(", "")
        updated_wallet_balance = updated_wallet_balance.replace(")", "")
        updated_wallet_balance = updated_wallet_balance.replace(",", "")
        updated_wallet_balance = int(updated_wallet_balance)

        # Create and send the embed with all the information
        embed = Embed(
            title="Withdrawal Successful", 
            description=f"You have successfully withdrawn {cash}{amount:,} from your bank.", 
            )
        embed.add_field(name="Withdrawn Amount", value=f"{cash}{amount:,}", inline=False)
        embed.add_field(name="Updated Bank Balance", value=f"{cash}{updated_bank_balance:,}/{cash}{bank_capacity:,}", inline=False)
        embed.add_field(name="Updated Wallet Balance", value=f"{cash}{updated_wallet_balance:,}", inline=False)
        embed.set_footer(text=f"{ctx.author.name}'s updated balances")

        await ctx.send(embed=embed)


    @commands.hybrid_command(
        name="deposit",
        description="Deposits money to your bank.",
        usage="deposit [amount]",
        aliases=["dep"],
    )
    async def deposit(self, ctx: Context, amount: int):
        if amount <= 0:
            await ctx.send("You can't deposit negative or zero money!")
            return

        # get the user's wallet balance
        wallet_balance = await db_manager.get_money(ctx.author.id)
        wallet_balance = str(wallet_balance)
        # remove the ( and ) and , from the wallet balance
        wallet_balance = wallet_balance.replace("(", "")
        wallet_balance = wallet_balance.replace(")", "")
        wallet_balance = wallet_balance.replace(",", "")
        wallet_balance = int(wallet_balance)

        # get the user's bank balance
        bank_balance = await db_manager.get_bank_balance(ctx.author.id)
        bank_balance = str(bank_balance)
        bank_balance = bank_balance.replace("(", "")
        bank_balance = bank_balance.replace(")", "")
        bank_balance = bank_balance.replace(",", "")
        bank_balance = int(bank_balance)

        # get the user's bank capacity
        bank_capacity = await db_manager.get_bank_capacity(ctx.author.id)
        bank_capacity = str(bank_capacity)
        bank_capacity = bank_capacity.replace("(", "")
        bank_capacity = bank_capacity.replace(")", "")
        bank_capacity = bank_capacity.replace(",", "")
        bank_capacity = int(bank_capacity)

        # check if the user has enough money in their wallet
        if wallet_balance < amount:
            await ctx.send("You don't have enough money in your wallet to deposit that much!")
            return
        # check if the deposit does not exceed the bank capacity
        elif bank_balance + amount > bank_capacity:
            await ctx.send("This deposit would exceed your bank's capacity!")
            return

        # if the user has enough money in their wallet and the deposit does not exceed the bank capacity, deposit the money
        await db_manager.remove_money(ctx.author.id, amount)
        await db_manager.add_to_bank(ctx.author.id, amount)

        # Get the updated balances
        updated_bank_balance = await db_manager.get_bank_balance(ctx.author.id)
        updated_wallet_balance = await db_manager.get_money(ctx.author.id)
        #remove the ( and ) and , from the updated balances
        updated_bank_balance = str(updated_bank_balance)
        updated_bank_balance = updated_bank_balance.replace("(", "")
        updated_bank_balance = updated_bank_balance.replace(")", "")
        updated_bank_balance = updated_bank_balance.replace(",", "")
        updated_bank_balance = int(updated_bank_balance)

        updated_wallet_balance = str(updated_wallet_balance)
        updated_wallet_balance = updated_wallet_balance.replace("(", "")
        updated_wallet_balance = updated_wallet_balance.replace(")", "")
        updated_wallet_balance = updated_wallet_balance.replace(",", "")
        updated_wallet_balance = int(updated_wallet_balance)

        # Create and send the embed with all the information
        embed = Embed(
            title="Deposit Successful", 
            description=f"You have successfully deposited {cash}{amount:,} to your bank.", 
            )
        embed.add_field(name="Deposited Amount", value=f"{cash}{amount:,}", inline=False)
        embed.add_field(name="Updated Bank Balance", value=f"{cash}{updated_bank_balance:,}/{cash}{bank_capacity:,}", inline=False)
        embed.add_field(name="Updated Wallet Balance", value=f"{cash}{updated_wallet_balance:,}", inline=False)
        embed.set_footer(text=f"{ctx.author.name}'s updated balances")

        await ctx.send(embed=embed)

    @commands.hybrid_command(
        name="balance",
        description="Displays your wallet and bank balance.",
        usage="balance",
        aliases=["bal"],
    )
    async def balance(self, ctx: Context):
        # get the user's wallet balance
        wallet_balance = await db_manager.get_money(ctx.author.id)
        wallet_balance = str(wallet_balance)
        # remove the ( and ) and , from the wallet balance
        wallet_balance = wallet_balance.replace("(", "")
        wallet_balance = wallet_balance.replace(")", "")
        wallet_balance = wallet_balance.replace(",", "")
        wallet_balance = int(wallet_balance)

        # get the user's bank balance
        bank_balance = await db_manager.get_bank_balance(ctx.author.id)
        bank_balance = str(bank_balance)
        bank_balance = bank_balance.replace("(", "")
        bank_balance = bank_balance.replace(")", "")
        bank_balance = bank_balance.replace(",", "")
        bank_balance = int(bank_balance)

        #get the user's bank capacity
        bank_capacity = await db_manager.get_bank_capacity(ctx.author.id)
        bank_capacity = str(bank_capacity)
        bank_capacity = bank_capacity.replace("(", "")
        bank_capacity = bank_capacity.replace(")", "")
        bank_capacity = bank_capacity.replace(",", "")
        bank_capacity = int(bank_capacity)

        profile = await db_manager.profile(ctx.author.id)
        locked = profile[33]


        # Create and send the embed with all the information
        embed = Embed(
            title=f"{ctx.author.name}'s Balances", 
            description=f"Here are your current balances.", 
            )
        if locked == True:
            embed.add_field(name="Wallet<:Padlock_Locked:1116772808110911498>", value=f"{cash}{wallet_balance:,}", inline=True)
        else:
            embed.add_field(name="Wallet<:Padlock_Unlocked:1116772713952981103>", value=f"{cash}{wallet_balance:,}", inline=True)
        embed.add_field(name="Bank", value=f"{cash}{bank_balance:,}/{cash}{bank_capacity:,}", inline=True)

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Bank(bot))



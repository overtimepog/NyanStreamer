import asyncio
import json
import os
import random
from io import BytesIO
from typing import Any, Optional, Tuple, Union

import aiohttp
import aiosqlite
import discord
import requests
from discord.ext import commands
from discord.ext.commands import Bot, Context
from PIL import Image, ImageChops, ImageDraw, ImageFont
from discord import Embed

from helpers import db_manager, battle
from num2words import num2words


cash = "✧"
async def bank(ctx: Context):
    pass

def format_number(number: int) -> str:
    """Format the number with commas and add the spelled out version."""
    return f"{number:,} ({num2words(number)})"

async def get_and_send_net_worth_embed(ctx: Context, user: discord.User):
    networth = 0

    # get the user inventory
    inventory = await db_manager.view_inventory(user.id)
    # cycle through the inventory, adding the value of each item to the networth
    inventory_networth = 0
    for item in inventory:
        price = item[3]
        price = int(price)
        amount = item[6]
        amount = int(amount)
        price = price * amount
        inventory_networth += price
    networth += inventory_networth

    # get the user balance
    wallet = await db_manager.get_money(user.id)
    wallet = str(wallet)
    # remove the ( and ) and , from the balance
    wallet = wallet.replace("(", "")
    wallet = wallet.replace(")", "")
    wallet = wallet.replace(",", "")
    wallet = int(wallet)
    networth += wallet

    # get the bank balance of the user
    bank = await db_manager.get_bank_balance(user.id)
    bank = str(bank)
    # remove the ( and ) and , from the bank balance
    bank = bank.replace("(", "")
    bank = bank.replace(")", "")
    bank = bank.replace(",", "")
    bank = int(bank)
    networth += bank

    # Create the embed
    embed = Embed(title=f"{user.name}'s Net Worth", description=f"Total net worth: **{cash}{format_number(networth)}**")
    embed.add_field(name="Inventory Worth", value=f"{cash}{format_number(inventory_networth)} ({(inventory_networth / networth) * 100:.2f}%)" if networth != 0 else "0 (0.00%)", inline=False)
    embed.add_field(name="Wallet Balance", value=f"{cash}{format_number(wallet)} ({(wallet / networth) * 100:.2f}%)" if networth != 0 else "0 (0.00%)", inline=False)
    embed.add_field(name="Bank Balance", value=f"{cash}{format_number(bank)} ({(bank / networth) * 100:.2f}%)" if networth != 0 else "0 (0.00%)", inline=False)

    # Send the embed
    await ctx.send(embed=embed)


async def get_user_net_worth(user: discord.User):
    networth = 0

    # get the user inventory
    inventory = await db_manager.view_inventory(user.id)
    # cycle through the inventory, adding the value of each item to the networth
    inventory_networth = 0
    for item in inventory:
        price = item[3]
        price = int(price)
        amount = item[6]
        amount = int(amount)
        price = price * amount
        inventory_networth += price
    networth += inventory_networth

    # get the user balance
    wallet = await db_manager.get_money(user.id)
    wallet = str(wallet)
    # remove the ( and ) and , from the balance
    wallet = wallet.replace("(", "")
    wallet = wallet.replace(")", "")
    wallet = wallet.replace(",", "")
    wallet = int(wallet)
    networth += wallet

    # get the bank balance of the user
    bank = await db_manager.get_bank_balance(user.id)
    bank = str(bank)
    # remove the ( and ) and , from the bank balance
    bank = bank.replace("(", "")
    bank = bank.replace(")", "")
    bank = bank.replace(",", "")
    bank = int(bank)
    networth += bank

    # Create a dictionary with all the values
    networth_dict = {
        "networth": networth,
        "inventory_networth": inventory_networth,
        "wallet": wallet,
        "bank": bank
    }
    return networth_dict
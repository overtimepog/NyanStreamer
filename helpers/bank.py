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

from helpers import db_manager, battle

async def bank(ctx: Context):
    pass

async def get_user_net_worth(ctx: Context, user: discord.User) -> int:
    networth = 0
    #get the user inventory
    inventory = await db_manager.view_inventory(user.id)
    #cycle through the inventory, adding the value of each item to the networth
    for item in inventory:
        price = item[3]
        price = int(price)
        networth += price

    #get the user balance
    wallet = await db_manager.get_money(user.id)
    wallet = str(wallet)
    #rmove the ( and ) and , from the balance
    wallet = wallet.replace("(", "")
    wallet = wallet.replace(")", "")
    wallet = wallet.replace(",", "")
    wallet = int(wallet)
    #add the balance to the networth
    networth += wallet
    #return the networth
    #get the bank balance of the user
    bank = await db_manager.get_bank_balance(user.id)
    bank = str(bank)
    #remove the ( and ) and , from the bank balance
    bank = bank.replace("(", "")
    bank = bank.replace(")", "")
    bank = bank.replace(",", "")
    bank = int(bank)
    #add the bank balance to the networth
    networth += bank
    #return the networth
    return networth
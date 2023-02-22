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

import random
from discord.ext.commands import Context

# assuming db_manager is already defined and connected to a database

async def mine(ctx: Context):
    # get all mineable items from the database
    minable_items = await db_manager.view_mineable_items()

    # check if the user has a pickaxe
    is_pickaxe_there = await db_manager.is_item_in_inventory(ctx.author.id, "pickaxe")
    if not is_pickaxe_there:
        await ctx.send("You need a pickaxe to mine! You can buy one in the shop.")
        return

    # possible phrases to describe the outcome
    outcome_phrases = [
        "You mined deep into the earth and found ",
        "Exploring the mine shaft, you discovered ",
        "As you worked your way through the tunnel, you unearthed ",
        "You mined through the rock face and found ",
        "Deep in the mine, you found ",
        "After hours of digging, you discovered ",
        "You mined and mined until you found ",
        "As you explored the mine, you stumbled upon ",
        "In the depths of the mine, you found ",
        "You delved into the earth and found ",
        "Wandering the mine tunnels, you chanced upon ",
        "Mining your way through the darkness, you discovered ",
        "Amidst the rocks and rubble, you spotted "
    ]

    # get the mine chance for each item in the minable_items list
    mine_items = []
    for item in minable_items:
        item_id = item[0]
        mine_chance = item[17]
        mine_items.append([item_id, mine_chance])

    # organize the mine items by their mine chance
    mine_items.sort(key=lambda x: x[1], reverse=True)

    # get the user's luck
    luck = await db_manager.get_luck(ctx.author.id)

    # roll a number between 1 and 100, the higher the luck, the higher the chance of getting a higher number,
    # the higher the number, the higher the chance of getting a better item, which is determined by the mine chance
    # of each item, the higher the mine chance, the higher the chance of getting that item
    roll = random.randint(1, 100) - luck

    # if the roll is greater than 100, set it to 100
    if roll > 100:
        roll = 100

    # if the roll is less than 1, set it to 1
    if roll < 1:
        roll = 1

    # get the items with the mine chance 0.01 or lower
    low_chance_items = []
    for item in mine_items:
        if item[1] <= 0.1:
            low_chance_items.append(item)

    mid_chance_items = []
    for item in mine_items:
        if item[1] > 0.1 and item[1] <= 0.5:
            mid_chance_items.append(item)

    high_chance_items = []
    for item in mine_items:
        if item[1] > 0.5 and item[1] <= 1:
            high_chance_items.append(item)

    # based on the roll, get the item
    if roll <= 10:
        item = random.choice(low_chance_items)
    elif roll > 10 and roll <= 50:
        item = random.choice(mid_chance_items)
    elif roll > 50 and roll <= 90:
        item = random.choice(high_chance_items)
    else:
        # they found nothing
        await ctx.send("You mined for hours, but found nothing.")
        return
    
    
    #get the item's info
    #roll a number between 1 and 15 to determine how many of the item they get
    amount = random.randint(1, 5)
    amount = amount + (luck // 10)
    if amount < 1:
        amount = 1
    if amount > 15:
        amount = 15
    #grant the item to the user
    await db_manager.add_item_to_inventory(ctx.author.id, item[0], amount)
    item_name = await db_manager.get_basic_item_name(item[0])
    item_emoji = await db_manager.get_basic_item_emote(item[0])
    #tell the user what they got
    await ctx.send(random.choice(outcome_phrases) + f"{item_emoji} **{item_name}** - {amount}")
    return
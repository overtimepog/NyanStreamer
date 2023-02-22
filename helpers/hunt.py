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

async def hunt(ctx: Context):
    firsthuntitems = await db_manager.view_huntable_items()
    #check if the user has a bow
    isbowThere = await db_manager.is_item_in_inventory(ctx.author.id, "huntingbow")
    if isbowThere == False or isbowThere == None or isbowThere == 0:
        await ctx.send("You need a Bow to go Hunting! You can buy one in the shop!")
        return

    #get the hunt chance for each item in the huntitems list
    huntItems = []
    for item in firsthuntitems:
        item_id = item[0]
        hunt_chance = item[16]
        huntItems.append([item_id, hunt_chance])

    #organize the hunt items by their hunt chance
    huntItems.sort(key=lambda x: x[1], reverse=True)
    #get the user's luck
    luck = await db_manager.get_luck(ctx.author.id)
    #make the luck an int
    luck = int(luck[0])

    #roll a number between 1 and 100, the higher the luck, the higher the chance of getting a higher number, the higher the number, the higher the chance of getting a better item, which is determined by the hunt chance of each item, the higher the hunt chance, the higher the chance of getting that item
    roll = random.randint(1, 100) - luck
    #if the roll is greater than 100, set it to 100
    if roll > 100:
        roll = 100
    
    #if the roll is less than 1, set it to 1
    if roll < 1:
        roll = 1
    
    #get the items with the hunt chance 0.01 or lower
    lowchanceitems = []
    for item in huntItems:
        if item[1] <= 0.1:
            lowchanceitems.append(item)

    midchanceitems = []
    for item in huntItems:
        if item[1] > 0.1 and item[1] <= 0.5:
            midchanceitems.append(item)

    highchanceitems = []
    for item in huntItems:
        if item[1] > 0.5 and item[1] <= 1:
            highchanceitems.append(item)

    #based on the roll, get the item
    if roll <= 10:
        item = random.choice(lowchanceitems)
    elif roll > 10 and roll <= 50:
        item = random.choice(midchanceitems)
    elif roll > 50 and roll <= 90:
        item = random.choice(highchanceitems)
    elif roll > 90:
        #they found nothing
        await ctx.send("You went Hunting and found nothing!")
        return

    #get the item's info
    #grant the item to the user
    await db_manager.add_item_to_inventory(ctx.author.id, item[0])
    #tell the user what they got
    await ctx.send(f"You went Hunting and found {item[1]}!")



    

    
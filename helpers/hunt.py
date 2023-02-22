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
        await ctx.send("You need a Bow to go Hunting!")
        return
    
    outcomePhrases = ["You ventured deep into the forest and stumbled upon, ", "Traversing the dense woodland, you discovered, ", "Exploring the forest floor, you found, ", "Amidst the trees and undergrowth, you spotted, ", "Making your way through the thicket, you came across, ", "Venturing off the beaten path, you uncovered, ", "You hiked through the forest and found, ", "Wandering among the trees, you chanced upon, ", "Following the sounds of the forest, you encountered, ", "Roaming through the woods, you discovered, ", "You delved into the heart of the forest and found, ", "Tracing the winding trails, you stumbled upon, ", "As you explored the forest canopy, you beheld, "]

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
        await ctx.send("You went Hunting and found nothing, Lol!")
        return

    #get the item's info
    #roll a number between 1 and 15 to determine how many of the item they get
    amount = random.randint(1, 5)
    amount = amount + (luck // 10)
    if amount < 1:
        amount = 1
    if amount > 10:
        amount = 10
    #grant the item to the user
    await db_manager.add_item_to_inventory(ctx.author.id, item[0], amount)
    item_name = await db_manager.get_basic_item_name(item[0])
    item_emoji = await db_manager.get_basic_item_emote(item[0])
    #tell the user what they got
    await ctx.send(random.choice(outcomePhrases) + f"{item_emoji} **{item_name}** - {amount}")
    return
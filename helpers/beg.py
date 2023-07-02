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
from typing import List, Tuple
cash = "✧"

def choose_outcome_based_on_chance(outcomes):
    total = sum(outcome['chance'] for outcome in outcomes)
    r = random.uniform(0, total)
    upto = 0
    for outcome in outcomes:
        if upto + outcome['chance'] >= r:
            return outcome
        upto += outcome['chance']
    assert False, "Shouldn't get here"

def choose_item_based_on_hunt_chance(items_with_chances):
    total = sum(w for i, w in items_with_chances)
    r = random.uniform(0, total)
    upto = 0
    for item, w in items_with_chances:
        if upto + w >= r:
            return item
        upto += w
    assert False, "Shouldn't get here"

async def beg(ctx: Context):
    with open('assets/beg.json') as f:
        data = json.load(f)
        begs = data['begs']

    beg = random.choice(begs)
    comment = random.choice(beg['comments'])
    outcome = choose_outcome_based_on_chance(beg['outcomes'])

    total = 0
    if outcome is not None:
        total = outcome['reward']

    # Add item finding mechanism here
    item_find_chance = random.random()  # Generates a random float between 0.0 and 1.0
    item_string = ""  # This will hold the item string if an item is found

    # Only try to find an item if the random chance is less than a certain threshold
    if item_find_chance < 0.3:  # Adjust this value to make finding items more or less rare
        firsthuntitems = await db_manager.view_huntable_items()
        huntItems = []
        for item in firsthuntitems:
            item_id = item[0]
            hunt_chance = item[16]
            huntItems.append([item_id, hunt_chance])

        luck = await db_manager.get_luck(ctx.author.id)
        huntItems = [(item, chance + luck / 100) for item, chance in huntItems]
        total_chance = sum(chance for item, chance in huntItems)
        huntItems = [(item, chance / total_chance) for item, chance in huntItems]

        item = choose_item_based_on_hunt_chance(huntItems)

        if item is not None:
            amount = random.randint(1, 5)
            amount = amount + (luck // 10)
            if amount < 1:
                amount = 1
            if amount > 10:
                amount = 10

            await db_manager.add_item_to_inventory(ctx.author.id, item, amount)
            item_id = item
            item_id = str(item_id)

            if item_id.split("_")[0] == "chest" or item_id == "chest":
                item_emoji = await db_manager.get_chest_icon
                item_name = await db_manager.get_chest_name(item_id)
            else:
                item_emoji = await db_manager.get_basic_item_emoji(item_id)
                item_name = await db_manager.get_basic_item_name(item_id)
            item_string = f"and **x{amount} {item_emoji}{item_name}**"

    # Now replace "{thing}" with the cash and item string (if any)
    comment = comment.replace("{thing}", f"**{cash}{total}** {item_string}")
    await db_manager.add_money(ctx.author.id, total)

    embed = discord.Embed(description=comment)
    embed.set_author(name=f"{beg['name']}")

    await ctx.send(embed=embed)

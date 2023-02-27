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
        try:
            item = random.choice(low_chance_items)
        except(IndexError):
            item = random.choice(mine_items)
    elif roll > 10 and roll <= 50:
        try:
            item = random.choice(mid_chance_items)
        except(IndexError):
            item = random.choice(low_chance_items)
    elif roll > 50 and roll <= 90:
        try:
            item = random.choice(high_chance_items)
        except(IndexError):
            item = random.choice(mid_chance_items)
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
    quest_id = await db_manager.get_user_quest(ctx.author.id)
    #if the user has a quest
    if quest_id != 0:
        objective = await db_manager.get_quest_objective_from_id(quest_id)
        quest_type = await db_manager.get_quest_type(quest_id)
        #if the quest type is kill
        if quest_type == "collect":
            #get the string of the monster name from the objective 
            objective = objective.split(" ")
            objective = objective[1]
            #if the objective is the same as the monster id
            if objective == item_id:
                #add 1 to the quest progress
                await db_manager.update_quest_progress(ctx.author.id, quest_id, 1)
                #get the quest progress
                quest_progress = await db_manager.get_quest_progress(ctx.author.id)
                #get the quest total
                quest_total = await db_manager.get_quest_total_from_id(quest_id)
                #if the quest progress is greater than or equal to the quest total
                if quest_progress >= quest_total:
                    #get the quest reward type and amount
                    quest_reward_type = await db_manager.get_quest_reward_type_from_id(quest_id)
                    quest_reward_amount = await db_manager.get_quest_reward_amount_from_id(quest_id)
                    #get the quest reward from the quest id
                    quest_reward = await db_manager.get_quest_reward_from_id(quest_id)
                    quest_xp_reward = await db_manager.get_quest_xp_reward_from_id(quest_id)
                    #add the quest xp reward to the users xp
                    await db_manager.add_xp(ctx.author.id, quest_xp_reward)
                    #if the quest reward type is gold, add the amount to the users gold
                    if quest_reward_type == "gold":
                        await db_manager.add_money(ctx.author.id, quest_reward_amount)
                        await ctx.send(f"You have completed the quest and been rewarded with {quest_reward_amount} gold!, and {quest_xp_reward} xp!")
                    #if the quest reward type is item get all the info on the item and add it to the users inventory
                    elif quest_reward_type == "item":
                        #get all the info on the item
                        item_name = await db_manager.get_basic_item_name(quest_reward)
                        item_price = await db_manager.get_basic_item_price(quest_reward)
                        item_type = await db_manager.get_basic_item_type(quest_reward)
                        item_emoji = await db_manager.get_basic_item_emote(quest_reward)
                        item_rarity = await db_manager.get_basic_item_rarity(quest_reward)
                        item_damage = await db_manager.get_basic_item_damage(quest_reward)
                        item_element = await db_manager.get_basic_item_element(quest_reward)
                        item_crit_chance = await db_manager.get_basic_item_crit_chance(quest_reward)
                        item_projectile = await db_manager.get_basic_item_projectile(quest_reward)
                        #convert the item name to str
                        item_name = str(item_name[0])
                        #convert the item price to int
                        item_price = int(item_price[0])
                        #convert the item type to str
                        item_type = str(item_type[0])
                        #convert the item emoji to str
                        item_emoji = str(item_emoji[0])
                        #convert the item rarity to str
                        item_rarity = str(item_rarity[0])
                        #convert the item damage to int
                        item_damage = int(item_damage[0])
                        #convert the item sub type to str
                        item_element = str(item_element[0])
                        #convert the item crit chance to int
                        item_crit_chance = int(item_crit_chance[0])
                        #convert the item projectile to str
                        item_projectile = str(item_projectile[0])
                        #add the item to the users inventory, with all the info needed for the function
                        await db_manager.add_item_to_inventory(ctx.author.id, quest_reward, quest_reward_amount)
                        await ctx.send(f"You have completed the quest and been rewarded with {item_name}!, and {quest_xp_reward} xp!")
                    #mark the quest as complete
                    await db_manager.mark_quest_completed(ctx.author.id, quest_id)
                    return
    else:
        return
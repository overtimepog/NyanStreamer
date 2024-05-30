import asyncio
import json
import os
import random
from io import BytesIO
from typing import Any, Optional, Tuple, Union, List

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
    outcomePhrases = ["You ventured deep into the forest and stumbled upon, ", "Traversing the dense woodland, you discovered, ", "Exploring the forest floor, you found, ", "Amidst the trees and undergrowth, you spotted, ", "Making your way through the thicket, you came across, ", "Venturing off the beaten path, you uncovered, ", "You hiked through the forest and found, ", "Wandering among the trees, you chanced upon, ", "Following the sounds of the forest, you encountered, ", "Roaming through the woods, you discovered, ", "You delved into the heart of the forest and found, ", "Tracing the winding trails, you stumbled upon, ", "As you explored the forest canopy, you beheld, "]

    # Get the hunt chance for each item in the huntitems list
    huntItems = [(item[0], item[16]) for item in firsthuntitems]

    # Get the user's luck
    luck = await db_manager.get_luck(ctx.author.id)

    # Apply the luck to the hunt chances
    huntItems = [(item_id, chance + luck) for item_id, chance in huntItems]

    # Normalize the chances
    total_chance = sum(chance for item_id, chance in huntItems)
    normalized_huntItems = [(item_id, (chance / total_chance) * 100) for item_id, chance in huntItems]

    # Choose an item based on hunt chances
    item = choose_item_based_on_hunt_chance(normalized_huntItems)

    if item is not None:
        # Determine the amount and cap it between 1 and 10
        amount = random.randint(1, 5) + (luck // 10)
        amount = max(1, min(amount, 10))

        # Grant the item to the user
        await db_manager.add_item_to_inventory(ctx.author.id, item, amount)

        # Get the item's emoji and name
        item_emoji = await db_manager.get_basic_item_emoji(item)
        item_name = await db_manager.get_basic_item_name(item)

        # Create and send the embed message
        embed = discord.Embed(title="Hunt", description=random.choice(outcomePhrases) + f"{item_emoji} **{item_name}**", color=0x00ff00)
        embed.add_field(name=f"Quantity", value=f"x{amount}", inline=False)
        await ctx.send(embed=embed)

        # Quest handling logic
        quest_id = await db_manager.get_user_quest(ctx.author.id)
        if quest_id != 0:
            objective = await db_manager.get_quest_objective_from_id(quest_id)
            quest_type = await db_manager.get_quest_type(quest_id)
            if quest_type == "collect":
                objective = objective.split(" ")[1]
                if objective == item:
                    await db_manager.update_quest_progress(ctx.author.id, quest_id, 1)
                    quest_progress = await db_manager.get_quest_progress(ctx.author.id)
                    quest_total = await db_manager.get_quest_total_from_id(quest_id)
                    if quest_progress >= quest_total:
                        quest_reward_type = await db_manager.get_quest_reward_type_from_id(quest_id)
                        quest_reward_amount = await db_manager.get_quest_reward_amount_from_id(quest_id)
                        quest_reward = await db_manager.get_quest_reward_from_id(quest_id)
                        quest_xp_reward = await db_manager.get_quest_xp_reward_from_id(quest_id)
                        await db_manager.add_xp(ctx.author.id, quest_xp_reward)
                        if quest_reward_type == "gold":
                            await db_manager.add_money(ctx.author.id, quest_reward_amount)
                            await ctx.send(f"You have completed the quest and been rewarded with {quest_reward_amount} gold and {quest_xp_reward} XP!")
                        elif quest_reward_type == "item":
                            await db_manager.add_item_to_inventory(ctx.author.id, quest_reward, quest_reward_amount)
                            item_name = await db_manager.get_basic_item_name(quest_reward)
                            await ctx.send(f"You have completed the quest and been rewarded with {item_name} and {quest_xp_reward} XP!")
                        await db_manager.mark_quest_completed(ctx.author.id, quest_id)
    else:
        await ctx.send("You went hunting and found nothing, Lol!")

def choose_item_based_on_hunt_chance(items_with_chances: List[Tuple[str, float]]):
    total = sum(chance for item_id, chance in items_with_chances)
    r = random.uniform(0, total)
    upto = 0
    for item_id, chance in items_with_chances:
        if upto + chance >= r:
            return item_id
        upto += chance
    assert False, "Shouldn't get here"
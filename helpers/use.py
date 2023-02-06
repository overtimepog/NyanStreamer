
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

async def useItem(self, ctx: Context, item_id: str):
        """
        This command will use an item.

        :param ctx: The context in which the command was called.
        :param item: The item that should be used.
        """
        user_id = ctx.message.author.id
        item_name = await db_manager.get_basic_item_name(item_id)
        item_damage = await db_manager.get_basic_item_damage(item_id)
        isUsable = await db_manager.is_basic_item_usable(item_id)
        #get the items effect
        item_effect = await db_manager.get_basic_item_effect(item_id)
        #get streamer item effect
        #check if the item is a streamer item
        isStreamerItem = await db_manager.check_streamer_item(item_id)
        isStreamerItemUsable = await db_manager.get_streamer_item_usable(item_id)
        if isStreamerItem == 1:
            if isStreamerItemUsable == True or isStreamerItemUsable == 1:
                streamer_item_effect = await db_manager.get_streamer_item_effect(item_id)
                if "heal" in streamer_item_effect:
                    #get the amount to heal the user by
                    heal_amount = int(streamer_item_effect[5:])
                    #heal the user
                    await db_manager.add_health(user_id, heal_amount)
                    #remove the item from the users inventory
                    await db_manager.remove_item_from_inventory(user_id, item_id)
                    await ctx.send(f"You used `{item_name}` and healed `{heal_amount}` health.")
                    return
            else:
                await ctx.send(f"`{item_name}` is not usable.")
                return
            
        if isUsable == 1:
            #remove item from inventory
            #before removing the item, check if the users health is full, if it is, don't remove the item
            user_health = await db_manager.get_health(user_id)
            user_max_health = 100
            if user_health == user_max_health:
                await ctx.send(f"You are already at full health.")
                return
            print(item_effect)
            #if item effect has the word heal in it then heal the user
            if "heal" in item_effect:
                #get the amount to heal the user by
                heal_amount = int(item_effect[5:])
                #heal the user
                await db_manager.add_health(user_id, heal_amount)
                #remove the item from the users inventory
                await db_manager.remove_item_from_inventory(user_id, item_id)
                #send a message
                await ctx.send(f"You used `{item_name}` and healed {heal_amount} health.")
            elif "revive" in item_effect:
                #revive the user
                await db_manager.set_alive(user_id)
                #heal the user to full health
                await db_manager.set_health(user_id, 100)
                #remove the item from the users inventory
                await db_manager.remove_item_from_inventory(user_id, item_id)
                #send a message
                await ctx.send(f"You used `{item_name}` and revived.")
        else:
            await ctx.send(f"`{item_name}` is not usable.")
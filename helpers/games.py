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

async def slots(ctx: Context, user, gamble):
    #create the slot machine, this will be a discord embed with 3 slots that will spin, through all the possible slot machine emojis, and then stop on 3 emojis
    #if the 3 emojis are the same, the user wins, if not, they lose
    #if the user wins, they get 3x their bet back
    #if the user loses, they lose their bet
    #if the user gets 2 of the same emojis, they get 1.5x their bet back

    #get the users money
    user_money = await db_manager.get_money(user.id)
    #check if the user has enough money to gamble
    if user_money < gamble:
        await ctx.send(f"You do not have enough money to gamble `{gamble}`.")
        return
    #remove the users money
    await db_manager.remove_money(user.id, gamble)
    #create the slot machine
    slot_machine = discord.Embed(title="Slot Machine", description=f"**{user.name}** is gambling `{gamble}`.", color=0x00ff00)
    slot_machine.set_author(name="Slots", icon_url=user.avatar_url)
    slot_machine.set_footer(text="Slots")
    slot_machine.add_field(name="Slot 1", value=":question:", inline=True)
    slot_machine.add_field(name="Slot 2", value=":question:", inline=True)
    slot_machine.add_field(name="Slot 3", value=":question:", inline=True)
    slot_machine_message = await ctx.send(embed=slot_machine)
    #create a list of all the possible slot machine emojis
    emoji = [
        ":apple:",
        ":cherries:",
        ":grapes:",
        ":lemon:",
        ":peach:",
        ":tangerine:",
    ]
    #edit the embed to show the emojis spinning
    #for every emoji in the list, edit the embed to show the emoji in the slot
    #SLOT 1
    for i in emoji:
        slot_machine.set_field_at(0, name="Slot 1", value=i, inline=True)
        await slot_machine_message.edit(embed=slot_machine)
        await asyncio.sleep(0.5)
    #get a random emoji from the list
    slot1 = random.choice(emoji)
    #edit the embed to show the emoji in the slot
    slot_machine.set_field_at(0, name="Slot 1", value=slot1, inline=True)
    await slot_machine_message.edit(embed=slot_machine)
    #for every emoji in the list, edit the embed to show the emoji in the slot
    
    #SLOT 2
    for i in emoji:
        slot_machine.set_field_at(1, name="Slot 2", value=i, inline=True)
        await slot_machine_message.edit(embed=slot_machine)
        await asyncio.sleep(0.5)
    #get a random emoji from the list
    slot2 = random.choice(emoji)
    #edit the embed to show the emoji in the slot
    slot_machine.set_field_at(1, name="Slot 2", value=slot2, inline=True)
    await slot_machine_message.edit(embed=slot_machine)
    #for every emoji in the list, edit the embed to show the emoji in the slot
    
    #SLOT 3
    for i in emoji:
        slot_machine.set_field_at(2, name="Slot 3", value=i, inline=True)
        await slot_machine_message.edit(embed=slot_machine)
        await asyncio.sleep(0.5)
    #get a random emoji from the list
    slot3 = random.choice(emoji)
    #edit the embed to show the emoji in the slot
    slot_machine.set_field_at(2, name="Slot 3", value=slot3, inline=True)
    await slot_machine_message.edit(embed=slot_machine)
    
    #edit the embed to show the emojis spinning
    
        
    
    
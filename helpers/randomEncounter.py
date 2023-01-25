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

#generate the channels for random encounters, first ask the user if they want to generate them
async def generate_channels(ctx: Context):
    print("Generating channels")
    guild = ctx.guild
    #check if the category is already in the channels
    #check if the category already exists
    category = discord.utils.get(guild.categories, name='DankStreamer')
    if category is None:
        created_category = await ctx.guild.create_category("DankStreamer")
        dungeon = await created_category.create_text_channel("dungeon")
        await ctx.send("Channels created, Sending Test Message")
        await dungeon.send("Hi, Welcome to DankStreamer, this is a random encounter channel, Monsters will randomly spawn here for you to fight and loot, have fun :)")
    else:
        print("Category already exists")
        await ctx.send("Channels Already Exist")
        
#delete the channels
async def delete_channels(ctx: Context):
    print("Deleting channels")
    guild = ctx.guild
    category = discord.utils.get(guild.categories, name='DankStreamer')
    dungeon = discord.utils.get(category.text_channels, name='dungeon')
    await dungeon.delete()
    await category.delete()
    await ctx.send("Channels Deleted")
        
#get alll the enimies from the database
async def get_enemies():
    print("Getting Enemies")
    enemies = await db_manager.get_all_enemies()
    return enemies

#generate a random enemy
async def generate_enemy(enemies):
    print("Generating Enemy")
    enemy = random.choice(enemies)
    type = enemy[7]
    type = str(type)
    #if the enemy is a boss, exclude it from the random choice
    return enemy

#generate an embed for the enemy

#get the dungion channel
async def get_dungeon_channel(ctx: Context):
    print("Getting dungeon Channel")
    guild = ctx.guild
    category = discord.utils.get(guild.categories, name='DankStreamer')
    dungeon = discord.utils.get(category.text_channels, name='dungeon')
    return dungeon

#put it all together
async def random_encounter(ctx: Context):
    print("Random Encounter")
    enemies = await get_enemies()
    enemy = await generate_enemy(enemies)
    print(enemy)
    emoji = enemy[4]
    emoji = str(emoji)
    #check if the emoji is a custom emoji or a normal emoji
    if emoji.startswith("<"):
        emoji = emoji[2:-1]
        print(emoji)
        basic_item_emote = emoji.replace("<", "")
        basic_item_emote = emoji.replace(">", "")
        colon_index = basic_item_emote.index(":")
        colon_index = basic_item_emote.index(":", colon_index + 1)
        # Create a new string starting from the character after the second colon
        new_s = basic_item_emote[colon_index + 1:]
        #remove evrything from the string, after the second :, then itll work :)
        print(new_s)
        emoji_url = f"https://cdn.discordapp.com/emojis/{new_s}.png"
    else:
        emoji = emoji
        print(emoji)
        emoji_unicode = ('{:X}'.format(ord(emoji)))
        emoji_unicode = emoji_unicode.lower()
        #make a web request to get the emoji name
        emoji_url = f"https://images.emojiterra.com/google/noto-emoji/v2.034/128px/{emoji_unicode}.png"
        
    print("Generating Embed")
    
    #get the enemy type
    type = enemy[7]
    type = str(type)
    #get the enemy rarity
    rarity = enemy[6]
    rarity = str(rarity)
    #based on the rarity, change the embed color
    if rarity == "Common":
        embed = discord.Embed(title=enemy[1], description=enemy[5], color=0x808080)
    elif rarity == "Uncommon":
        embed = discord.Embed(title=enemy[1], description=enemy[5], color=0x00B300)
    elif rarity == "Rare":
        embed = discord.Embed(title=enemy[1], description=enemy[5], color=0x0057C4)
    elif rarity == "Epic":
        embed = discord.Embed(title=enemy[1], description=enemy[5], color=0xa335ee)
    elif rarity == "Legendary":
        embed = discord.Embed(title=enemy[1], description=enemy[5], color=0xff8000)
    #if the enemy is a boss, add a boss tag to the embed
    if type == "Boss":
        embed.set_author(name="Boss")
        embed.title = f"{enemy[1]} (Boss)"
    embed.set_thumbnail(url=emoji_url)
    embed.add_field(name="Health", value=enemy[2], inline=True),
    embed.add_field(name="Attack", value=enemy[3], inline=True),
    dungeon = await get_dungeon_channel(ctx)
    if dungeon is None:
        print("Dungeon Channel not found")
    else:
        print("Sending Embed")
        dungeonEmbed = await dungeon.send(embed=embed)
        
        #react to the embed with the check emoji
        await dungeonEmbed.add_reaction("✅")
        
        #if the reaction is added, start the fight
        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) == '✅'
        try:
            reaction, user = await ctx.bot.wait_for('reaction_add', timeout=30.0, check=check)
        except asyncio.TimeoutError:
            await dungeon.send('Sorry, you took too long')
        else:
            await dungeon.send('Starting Fight')
            await battle.deathbattle_monster(dungeon, ctx.author.id, ctx.author.name, enemy[0], enemy[1])
    return enemy

#loop it
async def loop_random_encounters(ctx: Context):
    print("Looping Random Encounter")
    while True:
        await random_encounter(ctx)
        await asyncio.sleep(60)
    
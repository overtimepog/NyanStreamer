import aiosqlite
import requests
import aiohttp
import discord
from typing import Tuple, Any, Optional, Union
import random

from discord.ext import commands
from discord.ext.commands import Bot, Context
from helpers import db_manager
from PIL import Image, ImageChops, ImageDraw, ImageFont
import os
from io import BytesIO

async def deathbattle(ctx: Context, user1, user2):
    turnCount = 0
    #set each users isInCombat to true
    await db_manager.set_in_combat(user1)
    await db_manager.set_in_combat(user2)
    embed = discord.Embed(title="Battle", description="Battle between <@" + str(user1) + "> and <@" + str(user2) + ">", color=0x00ff00)
    msg = await ctx.send(embed=embed)

    #TODO: figure out how to get the path of this file without hardcoding it
    path = r"C:\Users\truen\OneDrive\Desktop\Stuff\projects\DankStreamer\images\battle_backround.png"
    background = Image.open(path)
    #Q, how do I get the path of this file
    #A, use os.path.dirname(__file__)

    #User 1
    user = discord.utils.get(ctx.guild.members, id=int(user1))
    avatar1url = user.avatar.url
    response = requests.get(avatar1url)
    avatar1 = Image.open(BytesIO(response.content))
    draw = ImageDraw.Draw(background)
    font = ImageFont.truetype("fonts/arial.ttf", 30)
    #draw the user's profile picture
    avatar1 = avatar1.resize((500, 500))
    background.paste(avatar1, (50, 320))
    #draw the user's name
    draw.text((70, 860), user.name, (0, 0, 0), font=font)

    #User 2
    user = discord.utils.get(ctx.guild.members, id=int(user2))
    avatar2url = user.avatar.url
    draw = ImageDraw.Draw(background)
    font = ImageFont.truetype("fonts/arial.ttf", 30)
    #draw the user's profile picture
    response = requests.get(avatar2url)
    avatar2 = Image.open(BytesIO(response.content))
    avatar2 = avatar2.resize((500, 500))
    background.paste(avatar2, (1300, 320))
    #draw the user's name
    draw.text((1070, 860), user.name, (0, 0, 0), font=font)

    #save the image
    background.save("images/battle.png")
    #send the image in chat
    await ctx.send(file=discord.File("images/battle.png"))
    #delete the image
    os.remove("images/battle.png")






    while await db_manager.is_alive(user1) and await db_manager.is_alive(user2):
        # User 1
        #get the equipped weapon
        user1_weapon = await db_manager.get_equipped_weapon(user1)
        if user1_weapon == None or user1_weapon == []:
            user1_weapon = "Fists"
            user1_damage = 100
        else:
            user1_damage = await db_manager.get_equipped_weapon_damage(user1)
        #get the equipped armor
        user1_armor = await db_manager.get_equipped_armor(user1)
        if user1_armor == None or user1_armor == []:
            user1_armor = "Clothes"
            user1_defense = 1
        else:
            user1_defense = await db_manager.get_equipped_armor_damage(user1)

        # User 2
        #get the equipped weapon
        user2_weapon = await db_manager.get_equipped_weapon(user2)
        if user2_weapon == None or user2_weapon == []:
            user2_weapon = "Fists"
            user2_damage = 2
        else:
            user2_damage = await db_manager.get_equipped_weapon_damage(user2)
        #get the equipped armor
        user2_armor = await db_manager.get_equipped_armor(user2)
        if user2_armor == None or user2_armor == []:
            user2_armor = "Clothes"
            user2_defense = 1
        else:
            user2_defense = await db_manager.get_equipped_armor_damage(user2)

        # Calculate damage eah user will do
        user1_damage = user1_damage - user2_defense
        user2_damage = user2_damage - user1_defense

        #if the damage is less than 0, set it to 0
        if user1_damage < 0:
            user1_damage = 0
        if user2_damage < 0:
            user2_damage = 0

        #set user 1's turns to any odd number
        if turnCount % 2 == 0:
            #user 1 attacks
            await db_manager.remove_health(user2, user1_damage)
            #send turn count
            #generate embed with turn count and damage
            embed = discord.Embed(title="Battle", description="Turn " + str(turnCount) + " | <@" + str(user1) + "> attacked <@" + str(user2) + "> for " + str(user1_damage) + " damage!", color=0x00ff00)
            await msg.edit(embed=embed)

        #set user 2's turns to any even number
        if turnCount % 2 == 1:
            #user 2 attacks
            await db_manager.remove_health(user1, user2_damage)
            #send turn count
            #generate embed with turn count and damage
            embed = discord.Embed(title="Battle", description="Turn " + str(turnCount) + " | <@" + str(user2) + "> attacked <@" + str(user1) + "> for " + str(user2_damage) + " damage!", color=0x00ff00)
            await msg.edit(embed=embed)

        user2_health = await db_manager.get_health(user2)
        user1_health = await db_manager.get_health(user1)
        #convert health to int
        #Q, how do I conert tuple to int?
        #A, you can't, you have to convert it to a string first
        user2_health = str(user2_health)
        user1_health = str(user1_health)

        #remove the () and , from the string
        user2_health = user2_health.replace("(", "")
        user2_health = user2_health.replace(")", "")
        user2_health = user2_health.replace(",", "")
        user1_health = user1_health.replace("(", "")
        user1_health = user1_health.replace(")", "")
        user1_health = user1_health.replace(",", "")

        #convert to int
        user2_health = int(user2_health)
        user1_health = int(user1_health)

        print("User 1 health: " + str(user1_health))
        print("User 2 health: " + str(user2_health))

        if user1_health <= 0:
            #set the users health to 0
            await db_manager.set_health(user1, 0)
            await db_manager.set_dead(user1)

        if user2_health <= 0:
            #set the users health to 0
            await db_manager.set_health(user2, 0)
            await db_manager.set_dead(user2)

        #add 1 to the turn count
        turnCount += 1

    if await db_manager.is_alive(user1):
        print("User 1 won!")
        embed = discord.Embed(title="Battle", description="<@" + str(user1) + "> won the battle!", color=0x00ff00)
        await msg.edit(embed=embed)
        await db_manager.set_not_in_combat(user1)
        await db_manager.set_not_in_combat(user2)
        return user1
    else:
        print("User 2 won!")
        embed = discord.Embed(title="Battle", description="<@" + str(user2) + "> won the battle!", color=0x00ff00)
        await msg.edit(embed=embed)
        #set both users isInCombat to false
        await db_manager.set_not_in_combat(user1)
        await db_manager.set_not_in_combat(user2)
        return user2
    


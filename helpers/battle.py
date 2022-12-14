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
import asyncio
from io import BytesIO
import json

async def deathbattle(ctx: Context, user1, user2, user1_name, user2_name):
    turnCount = 0
    #set each users isInCombat to true
    #TODO: figure out how to get the path of this file without hardcoding it
    #get the background image path
    imgpath = "images/battle_backround.png"
    fontPath = "fonts/G_ari_bd.ttf"
    
    #open the background image
    background = Image.open(imgpath)
    #Q, how do I get the path of this file
    #A, use os.path.dirname(__file__)

    #User 1
    user = discord.utils.get(ctx.guild.members, id=int(user1))
    avatar1url = user.avatar.url
    response = requests.get(avatar1url)
    avatar1 = Image.open(BytesIO(response.content))
    draw = ImageDraw.Draw(background)
    font = ImageFont.truetype(fontPath, 30)
    #draw the user's profile picture
    avatar1 = avatar1.resize((500, 500))
    background.paste(avatar1, (50, 320))
    #draw the user's name
    draw.text((70, 860), user.name, (0, 0, 0), font=font)

    #User 2
    user = discord.utils.get(ctx.guild.members, id=int(user2))
    avatar2url = user.avatar.url
    draw = ImageDraw.Draw(background)
    font = ImageFont.truetype(fontPath, 30)
    #draw the user's profile picture
    response = requests.get(avatar2url)
    avatar2 = Image.open(BytesIO(response.content))
    avatar2 = avatar2.resize((500, 500))
    background.paste(avatar2, (1300, 320))
    #draw the user's name
    draw.text((1070, 860), user.name, (0, 0, 0), font=font)    
    await db_manager.set_in_combat(user1)
    await db_manager.set_in_combat(user2)
    embed = discord.Embed(color=0x00ff00)
    user1_health = await db_manager.get_health(user1)
    user2_health = await db_manager.get_health(user2)
    #remove the () and , from the health
    user1_health = str(user1_health).replace("(", "")
    user1_health = str(user1_health).replace(")", "")
    user1_health = str(user1_health).replace(",", "")
    user2_health = str(user2_health).replace("(", "")
    user2_health = str(user2_health).replace(")", "")
    user2_health = str(user2_health).replace(",", "")
    embed.add_field(name=user1_name, value="Health: " + user1_health, inline=True)
    embed.add_field(name=user2_name, value="Health: " + user2_health, inline=True)
    prev_desc = None

    #save the image
    background.save("images/battle.png")
    #send the image in chat
    msg = await ctx.channel.send(file=discord.File("images/battle.png"), embed=embed)
    #delete the image
    os.remove("images/battle.png")
    
    #before the loop starts, set the burn turn to 0 for each user
    user1_burn_turn = 0
    user2_burn_turn = 0
    
    while await db_manager.is_alive(user1) and await db_manager.is_alive(user2):
        # User 1
        #get the equipped weapon
        user1_weapon = await db_manager.get_equipped_weapon(user1)
        print(user1_weapon)
        if user1_weapon == None or user1_weapon == []:
            user1_weapon_name = "Fists"
            user1_damage = 35
            user1_weapon_subtype = "None"
            #convert subtype to str
            user1_weapon_subtype = str(user1_weapon_subtype)
        else:
            user1_weapon_name = user1_weapon[0][2]
            #convert it to str
            user1_weapon_name = str(user1_weapon_name)
            user1_damage = user1_weapon[0][8]
            user1_weapon_subtype = user1_weapon[0][10]
            #convert subtype to str
            user1_weapon_subtype = str(user1_weapon_subtype)
        #get the equipped armor
        user1_armor = await db_manager.get_equipped_armor(user1)
        if user1_armor == None or user1_armor == []:
            user1_armor_name = "Clothes"
            user1_defense = 1
        else:
            user1_armor_name = user1_armor[0][2]
            user1_defense = user1_armor[0][8]

        # User 2
        #get the equipped weapon
        user2_weapon = await db_manager.get_equipped_weapon(user2)
        if user2_weapon == None or user2_weapon == []:
            user2_weapon_name = "Fists"
            user2_damage = 2
            user2_weapon_subtype = "None"
            #convert subtype to str
            user2_weapon_subtype = str(user2_weapon_subtype)
        else:
            user2_weapon_name = user2_weapon[0][2]
            #convert it to str
            user2_weapon_name = str(user2_weapon_name)
            user2_damage = user2_weapon[0][8]
            user2_weapon_subtype = user2_weapon[0][10]
            #convert subtype to str
            user2_weapon_subtype = str(user2_weapon_subtype)
        #get the equipped armor
        user2_armor = await db_manager.get_equipped_armor(user2)
        if user2_armor == None or user2_armor == []:
            user2_armor_name = "Clothes"
            user2_defense = 1
        else:
            user2_armor_name = user2_armor[0][2]
            user2_defense = user2_armor[0][8]

        # Calculate damage each user will do
        user1_damage = user1_damage - user2_defense
        user2_damage = user2_damage - user1_defense

        #grab the crit chance of each user and roll a random number between 1 and 100 to see if they crit
        if user1_weapon_name == "Fists":
            user1_crit = "0%"
        else:
            user1_crit = user1_weapon[0][11]

        if user2_weapon_name == "Fists":
            user2_crit = "0%"
        else:
            user2_crit = user2_weapon[0][11]

        #remove the % from the crit chance
        user1_crit = str(user1_crit).replace("%", "")
        user2_crit = str(user2_crit).replace("%", "")
        #convert the crit chance to an int
        user1_crit = int(user1_crit)
        user2_crit = int(user2_crit)
        user1_roll = random.randint(1, 100)
        user2_roll = random.randint(1, 100)
        #if the roll is equal to the crit chance, double the damage\
        if user1_roll <= user1_crit:
            user1_damage = user1_damage * 2
        if user2_roll <= user2_crit:
            user2_damage = user2_damage * 2


        #if the damage is less than 0, set it to 0
        if user1_damage < 0:
            user1_damage = 0
        if user2_damage < 0:
            user2_damage = 0

        #set user 1's turns to any odd number
        if turnCount % 2 == 0:
            #if its been two turns since the user was set on fire, remove the burning status
            if user1_burn_turn != None and turnCount - user1_burn_turn >= 2:
                user1_burn_turn = None
                db_manager.set_user_not_burning(user1)
            #user 1 attacks
            await db_manager.remove_health(user2, user1_damage)
            #have the user have a 1/10 chance of being set on fire
            isSetONFire = random.randint(1, 10)
            #make embed with the previous description plus the new description
            if prev_desc == None:
                prev_desc = ""
            #if they crit, add a (crit) to the end of the damage
            if user1_roll <= user1_crit:
                Newdescription = prev_desc + "\n" + "__" + user1_name + "__ hit a crit on __" + user2_name + "__ with __" + user1_weapon_name + "__ for __" + str(user1_damage) + "__ damage (crit)"
            #if the sub type is Fire tell the user they were set on fire and add a (burning) to the end of the damage
            elif user1_weapon_subtype == "Fire" and isSetONFire == 1:
                Newdescription = prev_desc + "\n" + "__" + user1_name + "__ set __" + user2_name + "__ on fire with __" + user1_weapon_name + "__ for __" + str(user1_damage) + "__ damage (burning) ends in 2 turns"
                #set the users burn status to true
                await db_manager.set_user_burning(user2)
                #mark the turn the user was set on fire
                user2_burn_turn = turnCount
                
            else:
                #import User2 promts from assets/user1Promts.json
                with open("assets/user1Promts.json") as f:
                    user1Promts = json.load(f)
                #get a random user1 promt
                user1Promt = random.choice(user1Promts)
                #convert the promt to a string
                user1Promt = str(user1Promt)
                #replace the {user2_name} with the user2 name
                #convert both names to strings
                user1_name = str(user1_name)
                user2_name = str(user2_name)
                user1Promt = user1Promt.replace("{user2_name}", "__" + user2_name + "__")
                #replace {user1_name} with the user1 name
                user1Promt = user1Promt.replace("{user1_name}", "__" + user1_name + "__")
                #replace the {user2_weapon_name} with the user2 weapon
                user1Promt = user1Promt.replace("{user1_weapon_name}", "__" + user1_weapon_name + "__")
                #replace the {user2_damage} with the user2 damage
                user1Promt = user1Promt.replace("{user1_weapon_damage}", "__" + str(user1_damage) + "__")
                
                #add the user2 promt to the new description
                
                Newdescription = prev_desc + "\n" + f"{user1Promt}"
            #convert the embed to a string
            Newdescription = str(Newdescription)
            #if there are more than 4 lines in the embed, remove the first line
            if Newdescription.count("\n") > 3:
                Newdescription = Newdescription.split("\n", 1)[1]
            embed = discord.Embed(description=f"{Newdescription}", color=0x00ff00)
            #edit the embed feilds to include the new health
            user1_health = await db_manager.get_health(user1)
            user2_health = await db_manager.get_health(user2)
            #remove the () and , from the health
            user1_health = str(user1_health).replace("(", "")
            user1_health = str(user1_health).replace(")", "")
            user1_health = str(user1_health).replace(",", "")
            user2_health = str(user2_health).replace("(", "")
            user2_health = str(user2_health).replace(")", "")
            user2_health = str(user2_health).replace(",", "")

            #comvert the health to an int
            user1_health = int(user1_health)
            user2_health = int(user2_health)

            if user1_health < 0:
                user1_health = 0
            if user2_health < 0:
                user2_health = 0

            user1_health = str(user1_health)
            user2_health = str(user2_health)
            
            if await db_manager.check_user_burning(user1):
                await db_manager.remove_health(user1, 5)
                #add a (burning) to the users health
                user1_health = user1_health + " (burning)"
                #mark down the turn count when the user was set on fire
                
            if await db_manager.check_user_burning(user2):
                await db_manager.remove_health(user2, 5)
                #add a (burning) to the users health
                user2_health = user2_health + " (burning)"
                #mark down the turn count when the user was set on fire
            
            #edit the embed feilds to include the new health
            embed.add_field(name=user1_name, value="Health: " + user1_health, inline=True)
            embed.add_field(name=user2_name, value="Health: " + user2_health, inline=True)
            prev_desc = Newdescription
            #Q, whats the hex color for green
            #A, 0x00ff00
            await msg.edit(embed=embed)

        #set user 2's turns to any even number
        if turnCount % 2 == 1:
            #if its been 2 turns since the user was set on fire, remove the burning status
            if user2_burn_turn != None and turnCount - user2_burn_turn >= 2:
                user2_burn_turn = None
                await db_manager.set_user_not_burning(user2)
            #user 2 attacks
            await db_manager.remove_health(user1, user2_damage)
            #roll a 1/10 chance for the user to be set on fire
            isSetONFire = random.randint(1, 10)
            #make embed with the previous description plus the new description
            if prev_desc == None:
                prev_desc = ""
            #if they crit, add a (crit) to the end of the damage
            if user2_roll <= user2_crit:
                Newdescription = prev_desc + "\n" + "__" + user2_name + "__ hit a crit on __" + user1_name + "__ with __" + user2_weapon_name + "__ for __" + str(user2_damage) + "__ damage (crit)"
            #if the sub type is Fire tell the user they were set on fire and add a (burning) to the end of the damage
            elif user2_weapon_subtype == "Fire" and isSetONFire == 1:
                Newdescription = prev_desc + "\n" + "__" + user2_name + "__ set __" + user1_name + "__ on fire with __" + user2_weapon_name + "__ for __" + str(user2_damage) + "__ damage (burning) ends in 2 turns"
                #set the users burn status to true
                await db_manager.set_user_burning(user1)
                #mark down the turn count when the user was set on fire
                user1_burn_turn = turnCount
            else:
                #do the same thing as user 1 but with user 2
                with open("assets/user2Promts.json") as f:
                    user2Promts = json.load(f)
                #get a random user2 promt
                user2Promt = random.choice(user2Promts)
                #convert the promt to a string
                user2Promt = str(user2Promt)
                #replace the {user1_name} with the user1 name
                #convert both names to strings
                user1_name = str(user1_name)
                user2_name = str(user2_name)
                user2Promt = user2Promt.replace("{user1_name}", "__" + user1_name + "__")
                #replace {user2_name} with the user2 name
                user2Promt = user2Promt.replace("{user2_name}", "__" + user2_name + "__")
                #replace the {user2_weapon_name} with the user1 weapon
                user2Promt = user2Promt.replace("{user2_weapon_name}", "__" + user2_weapon_name + "__")
                #replace the {user2_damage} with the user1 damage
                user2Promt = user2Promt.replace("{user2_weapon_damage}", "__" + str(user2_damage) + "__")
                Newdescription = prev_desc + "\n" + f"{user2Promt}"
            Newdescription = str(Newdescription)
            #if there are more than 4 lines in the embed, remove the first line
            if Newdescription.count("\n") > 3:
                Newdescription = Newdescription.split("\n", 1)[1]
            embed = discord.Embed(description=f"{Newdescription}", color=0xff0000)
            #Q, whats the hex color for yellow
            #A, 0xffff00
            #edit the embed feilds to include the new health
            user1_health = await db_manager.get_health(user1)
            user2_health = await db_manager.get_health(user2)
            #remove the () and , from the health
            user1_health = str(user1_health).replace("(", "")
            user1_health = str(user1_health).replace(")", "")
            user1_health = str(user1_health).replace(",", "")
            user2_health = str(user2_health).replace("(", "")
            user2_health = str(user2_health).replace(")", "")
            user2_health = str(user2_health).replace(",", "")

            #comvert the health to an int
            user1_health = int(user1_health)
            user2_health = int(user2_health)
            #if the health is less than 0 or 0, set it to 0 and break the loop
            if user1_health <= 0:
                user1_health = 0
                break
            if user2_health <= 0:
                user2_health = 0
                break

            user1_health = str(user1_health)
            user2_health = str(user2_health)
            
            if await db_manager.check_user_burning(user2):
                await db_manager.remove_health(user2, 5)
                #add a (burning) to the users health
                user2_health = user2_health + " (burning)"
                #mark down the turn count when the user was set on fire
                
            if await db_manager.check_user_burning(user1):
                await db_manager.remove_health(user1, 5)
                #add a (burning) to the users health
                user1_health = user1_health + " (burning)"
                #mark down the turn count when the user was set on fire
            
            
            #edit the embed feilds to include the new health
            embed.add_field(name=user1_name, value="Health: " + user1_health, inline=True)
            embed.add_field(name=user2_name, value="Health: " + user2_health, inline=True)
            prev_desc = Newdescription
            #Q, whats the hex color for green
            #A, 0x00ff00
            await msg.edit(embed=embed)

        #add 1 to the turn count
        #sleep for 2 seconds
        turnCount += 1
        await asyncio.sleep(2)

    if await db_manager.is_alive(user1):
        #once a user wins, set both users isInCombat to false, and edit the embed to show who won
        print("User 1 won!")
        #set new description to the previous description plus the winner
        Newdescription = prev_desc + "\n" + "__" + user1_name + "__ won!"
        Newdescription = str(Newdescription)
        #if there are more than 4 lines in the embed, remove the first line
        if Newdescription.count("\n") > 3:
            Newdescription = Newdescription.split("\n", 1)[1]
        embed = discord.Embed(description=f"{Newdescription}", color=0xffff00)
        #edit the embed feilds to include the new health
        user1_health = await db_manager.get_health(user1)
        user2_health = await db_manager.get_health(user2)
        #remove the () and , from the health
        user1_health = str(user1_health).replace("(", "")
        user1_health = str(user1_health).replace(")", "")
        user1_health = str(user1_health).replace(",", "")
        user2_health = str(user2_health).replace("(", "")
        user2_health = str(user2_health).replace(")", "")
        user2_health = str(user2_health).replace(",", "")
        #convert to int
        user1_health = int(user1_health)
        user2_health = int(user2_health)
        #if the user is dead, set their health to 0
        if user1_health <= 0:
            user1_health = 0
        if user2_health <= 0:
            user2_health = 0

        #convert back to string
        user1_health = str(user1_health)
        user2_health = str(user2_health)
        
        #edit the embed feilds to include the new health
        embed.add_field(name=user1_name, value="Health: " + user1_health, inline=True)
        embed.add_field(name=user2_name, value="Health: " + user2_health, inline=True)

        await db_manager.set_not_in_combat(user1)
        await db_manager.set_not_in_combat(user2)


        await msg.edit(embed=embed)

        return user1
    else:
        print("User 2 won!")
        #set new description to the previous description plus the winner
        Newdescription = prev_desc + "\n" + "__" + user2_name + "__ won!"
        Newdescription = str(Newdescription)
        #if there are more than 4 lines in the embed, remove the first line
        if Newdescription.count("\n") > 3:
            Newdescription = Newdescription.split("\n", 1)[1]
        embed = discord.Embed(description=f"{Newdescription}", color=0xffff00)
        #edit the embed feilds to include the new health
        user1_health = await db_manager.get_health(user1)
        user2_health = await db_manager.get_health(user2)
        #remove the () and , from the health
        user1_health = str(user1_health).replace("(", "")
        user1_health = str(user1_health).replace(")", "")
        user1_health = str(user1_health).replace(",", "")
        user2_health = str(user2_health).replace("(", "")
        user2_health = str(user2_health).replace(")", "")
        user2_health = str(user2_health).replace(",", "")
        #convert to int
        user1_health = int(user1_health)
        user2_health = int(user2_health)
        #if the user is dead, set their health to 0
        if user1_health <= 0:
            user1_health = 0
        if user2_health <= 0:
            user2_health = 0

        #convert back to string
        user1_health = str(user1_health)
        user2_health = str(user2_health)
        
        #edit the embed feilds to include the new health
        embed.add_field(name=user1_name, value="Health: " + user1_health, inline=True)
        embed.add_field(name=user2_name, value="Health: " + user2_health, inline=True)

        await msg.edit(embed=embed)

        await db_manager.set_not_in_combat(user1)
        await db_manager.set_not_in_combat(user2)
        return user2
    


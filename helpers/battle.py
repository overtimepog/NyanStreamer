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

from helpers import db_manager, randomEncounter

#-------------------Death Battle-------------------#
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
    
    #before the loop starts, set the burn turn, poison turn, paralyze turn, and freeze turn to 0
    user1_burn_turn = 0
    user2_burn_turn = 0
    user1_poison_turn = 0
    user2_poison_turn = 0
    user1_paralyze_turn = 0
    user2_paralyze_turn = 0
    
    
    while await db_manager.is_alive(user1) and await db_manager.is_alive(user2):
        # User 1
        #get the equipped weapon
        user1_weapon = await db_manager.get_equipped_weapon(user1)
        #print(user1_weapon)
        if user1_weapon == None or user1_weapon == []:
            user1_weapon_name = "Fists"
            user1_damage = 1
            user1_weapon_subtype = "None"
            #convert subtype to str
            user1_weapon_subtype = str(user1_weapon_subtype)
            user1_weapon_projectile = user1_weapon[0][12]
            #convert projectile to str
            user1_weapon_projectile = str(user1_weapon_projectile)
            if user1_weapon_projectile == "Arrow":
                user1_arrows = await db_manager.get_arrows(user1)
                if user1_arrows == None or user1_arrows == [] or user1_arrows == 0:
                    #if the user doesn't have arrows, set the weapon to fists, and tell the user they don't have arrows
                    await ctx.channel.send(user1_name + " you don't have any arrows!")
                    user1_weapon_name = "Fists"
                    user1_damage = 2
                    user1_weapon_subtype = "None"
                    #convert subtype to str
                    user1_weapon_subtype = str(user1_weapon_subtype)
                else:
                    #if the user has arrows, tell the user how many they have
                    await ctx.channel.send(user1_name + " you have " + str(user1_arrows) + " arrows!")
            
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
            #if the users weapon has the item_projectile arrow, make sure the user has arrows
            user2_weapon_projectile = user2_weapon[0][12]
            #convert projectile to str
            user2_weapon_projectile = str(user2_weapon_projectile)
            if user2_weapon_projectile == "Arrow":
                user2_arrows = await db_manager.get_arrows(user2)
                if user2_arrows == None or user2_arrows == [] or user2_arrows == 0:
                    #if the user doesn't have arrows, set the weapon to fists, and tell the user they don't have arrows
                    await ctx.channel.send(user2_name + " you don't have any arrows!")
                    user2_weapon_name = "Fists"
                    user2_damage = 2
                    user2_weapon_subtype = "None"
                    #convert subtype to str
                    user2_weapon_subtype = str(user2_weapon_subtype)
                else:
                    #if the user has arrows, tell the user how many they have
                    await ctx.channel.send(user2_name + " you have " + str(user2_arrows) + " arrows!")

                
            #if the users weapon 
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

            #if its been 2 turns since the user was poisoned, remove the poisoned status
            if user1_poison_turn != None and turnCount - user1_poison_turn >= 2:
                user1_poison_turn = None
                db_manager.set_user_not_poisoned(user1)

            #if its been 1 turn since the user was paralyzed, remove the paralyzed status
            if user1_paralyze_turn != None and turnCount - user1_paralyze_turn >= 1:
                user1_paralyze_turn = None
                db_manager.set_user_not_paralyzed(user1)
    
            #user 1 attacks
            
            #if the user is using a projectile weapon, remove an arrow
            if user1_weapon_projectile == "Arrow":
                await db_manager.remove_item_from_inventory(user1, "Arrow", 1)
            await db_manager.remove_health(user2, user1_damage)
            #have the user have a 1/10 chance of being set on fire
            isSetONFire = random.randint(1, 10)
            #have the user have a 1/10 chance of being paralyzed
            isPoisoned = random.randint(1, 10)
            #a 1/10 chance of being paralyzed
            isParalyzed = random.randint(1, 10)
            #make embed with the previous description plus the new description
            if prev_desc == None:
                prev_desc = ""
            #if they crit, add a (crit) to the end of the damage
            if user1_roll <= user1_crit:
                Newdescription = prev_desc + "\n" + "__" + user1_name + "__ hit a crit on __" + user2_name + "__ with __" + user1_weapon_name + "__ for __" + str(user1_damage) + "__ damage (crit)"
            #if the sub type is Fire tell the user they were set on fire and add a (burning) to the end of the damage
            elif user1_weapon_subtype == "Fire" and isSetONFire == 1:
                Newdescription = prev_desc + "\n" + "__" + user1_name + "__ set __" + user2_name + "__ on fire <:flame1:1061287587395948634> with __" + user1_weapon_name + "__ for __" + str(user1_damage) + "__ plus 1 damage per turn (burning)"
                #set the users burn status to true
                await db_manager.set_user_burning(user2)
                #mark the turn the user was set on fire
                user2_burn_turn = turnCount
                
            #if the user is poisoned, tell the user they were poisoned, skip their turn and add a (poisoned) to the end of the damage
            elif user1_weapon_subtype == "Poison" and isPoisoned == 1:
                Newdescription = prev_desc + "\n" + "__" + user1_name + "__ poisoned <:poisoned:1061287780652691466> __" + user2_name + "__  with __" + user1_weapon_name + "__ for __" + str(user1_damage) + "__ plus 3 damage per turn (poisoned)"
                #set the users poison status to true
                await db_manager.set_user_poisoned(user2)
                #mark the turn the user was poisoned
                user2_poison_turn = turnCount

            #if the subtype is paralyze, tell the user they were paralyzed and skip their turn
            elif user1_weapon_subtype == "Paralyze" and isParalyzed == 1:
                Newdescription = prev_desc + "\n" + "__" + user1_name + "__ paralyzed <:paralyzed:1061287659722510419> __" + user2_name + "__  with __" + user1_weapon_name + "__ for __" + str(user1_damage) + "__ they wont be able to attack for a turn (paralyzed)"
                #set the users poison status to true
                await db_manager.set_user_paralyzed(user2)
                #mark the turn the user was poisoned
                user2_paralyze_turn = turnCount
                #skip the users turn
                turnCount += 1
                
            else:
                #import User2 promts from assets/user1Promts.json
                with open("assets/user1Promts.json") as f:
                    user1Promts = json.load(f)
                    
                #if the user is using a projectile weapon use the projectile promts
                if user1_weapon_projectile == "Arrow":
                    #import User2 promts from assets/user1Promts.json
                    with open("assets/user1ProjectilePromts.json") as f:
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
                
                #if the user is using a projectile weapon, replace the {user1_projectile} with the projectile
                if user1_weapon_projectile == "Arrow":
                    user1Promt = user1Promt.replace("{user1_projectile}", "__" + user1_weapon_projectile + "__")
                    
                #add the user2 promt to the new description
                
                Newdescription = prev_desc + "\n" + f"{user1Promt}"
            #convert the embed to a string
            Newdescription = str(Newdescription)
            #if there are more than 4 lines in the embed, remove the first line
            if Newdescription.count("\n") >= 3:
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
                await db_manager.remove_health(user1, 1)
                #add a (burning) to the users health
                user1_health = user1_health + " (burning)"
                #mark down the turn count when the user was set on fire
                
            if await db_manager.check_user_burning(user2):
                await db_manager.remove_health(user2, 1)
                #add a (burning) to the users health
                user2_health = user2_health + " (burning)"
                #mark down the turn count when the user was set on fire

            if await db_manager.check_user_poisoned(user1):
                await db_manager.remove_health(user1, 3)
                #add a (poisoned) to the users health
                user1_health = user1_health + " (poisoned)"
                #mark down the turn count when the user was set on fire
            
            if await db_manager.check_user_poisoned(user2):
                await db_manager.remove_health(user2, 3)
                #add a (poisoned) to the users health
                user2_health = user2_health + " (poisoned)"
                #mark down the turn count when the user was set on fire
                
            if await db_manager.check_user_paralyzed(user1):
                #add a (paralyzed) to the users health
                user1_health = user1_health + " (paralyzed)"
                
            if await db_manager.check_user_paralyzed(user2):
                #add a (paralyzed) to the users health
                user2_health = user2_health + " (paralyzed)"
            
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

            if user2_poison_turn != None and turnCount - user2_poison_turn >= 2:
                user2_poison_turn = None
                await db_manager.set_user_not_poisoned(user2)
            
            #after 1 turn, remove the paralyzed status
            if user2_paralyze_turn != None and turnCount - user2_paralyze_turn >= 1:
                user2_paralyze_turn = None
                await db_manager.set_user_not_paralyzed(user2)

            #user 2 attacks
            await db_manager.remove_health(user1, user2_damage)
            #roll a 1/10 chance for the user to be set on fire
            isSetONFire = random.randint(1, 10)
            isPoisoned = random.randint(1, 10)
            isParalyzed = random.randint(1, 10)
            #make embed with the previous description plus the new description
            if prev_desc == None:
                prev_desc = ""
            #if they crit, add a (crit) to the end of the damage
            if user2_roll <= user2_crit:
                Newdescription = prev_desc + "\n" + "__" + user2_name + "__ hit a crit on __" + user1_name + "__ with __" + user2_weapon_name + "__ for __" + str(user2_damage) + "__ damage (crit)"
            #if the sub type is Fire tell the user they were set on fire and add a (burning) to the end of the damage
            elif user2_weapon_subtype == "Fire" and isSetONFire == 1:
                Newdescription = prev_desc + "\n" + "__" + user2_name + "__ set __" + user1_name + "__ on fire <:flame1:1061287587395948634> with __" + user2_weapon_name + "__ for __" + str(user2_damage) + "__ plus 1 damage per turn (burning)"
                #set the users burn status to true
                await db_manager.set_user_burning(user1)
                #mark down the turn count when the user was set on fire
                user1_burn_turn = turnCount
            #if the sub type is Poison tell the user they were set on fire and add a (poisoned) to the end of the damage

            elif user2_weapon_subtype == "Poison" and isPoisoned == 1:
                Newdescription = prev_desc + "\n" + "__" + user2_name + "__ poisoned <:poisoned:1061287780652691466> __" + user1_name + "__ with __" + user2_weapon_name + "__ for __" + str(user2_damage) + "__ plus 3 damage per turn (poisoned)"
                #set the users poison status to true
                await db_manager.set_user_poisoned(user1)
                #mark down the turn count when the user was set on fire
                user1_poison_turn = turnCount
                
            #if the sub type is paralysis tell the user they were set on paralyzed and add a (paralyzed) to the end of the damage
            elif user2_weapon_subtype == "Paralysis" and isParalyzed == 1:
                Newdescription = prev_desc + "\n" + "__" + user2_name + "__ paralyzed <:paralyzed:1061287659722510419> __" + user1_name + "__ with __" + user2_weapon_name + "__ for __" + str(user2_damage) + "__ they wont be able to attack for a turn (paralyzed)"
                #set the users paralysis status to true
                await db_manager.set_user_paralyzed(user1)
                #skip the users turn
                #save the turn count when the user was paralyzed
                user1_paralyze_turn = turnCount
                turnCount = turnCount + 1
            else:
                #do the same thing as user 1 but with user 2
                with open("assets/user2Promts.json") as f:
                    user2Promts = json.load(f)
                    
                if user2_weapon_projectile == "Arrow":
                    #import User2 promts from assets/user1Promts.json
                    with open("assets/user2ProjectilePromts.json") as f:
                        user1Promts = json.load(f)
                    
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
                
                #if the user is using a projectile weapon, replace the {user1_projectile} with the projectile
                if user2_weapon_projectile == "Arrow":
                    user2Promt = user2Promt.replace("{user2_projectile}", "__" + user2_weapon_projectile + "__")
                    
                    
                Newdescription = prev_desc + "\n" + f"{user2Promt}"
            Newdescription = str(Newdescription)
            #if there are more than 4 lines in the embed, remove the first line
            if Newdescription.count("\n") >= 3:
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
                await db_manager.remove_health(user2, 1)
                #add a (burning) to the users health
                user2_health = user2_health + " (burning)"
                #mark down the turn count when the user was set on fire
                
            if await db_manager.check_user_burning(user1):
                await db_manager.remove_health(user1, 1)
                #add a (burning) to the users health
                user1_health = user1_health + " (burning)"
                #mark down the turn count when the user was set on fire

            if await db_manager.check_user_poisoned(user1):
                await db_manager.remove_health(user1, 3)
                #add a (poisoned) to the users health
                user1_health = user1_health + " (poisoned)"
                #mark down the turn count when the user was set on fire
            
            if await db_manager.check_user_poisoned(user2):
                await db_manager.remove_health(user2, 3)
                #add a (poisoned) to the users health
                user2_health = user2_health + " (poisoned)"
                #mark down the turn count when the user was set on fire
                
            if await db_manager.check_user_paralyzed(user1):
                user1_health = user1_health + " (paralyzed)"
            
            if await db_manager.check_user_paralyzed(user2):
                user2_health = user2_health + " (paralyzed)"
            
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
        Newdescription = prev_desc + "\n" + "🏆" + user1_name + " won!"
        Newdescription = str(Newdescription)
        #if there are more than or exactly 4 lines in the embed, remove the first line
        if Newdescription.count("\n") >= 3:
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
        
        #do the same thing for the other user
        xp_granted = random.randint(10, 20)
        coins_granted = random.randint(10, 20)
        #grant the user a random amount of xp between 10 and 20
        await db_manager.add_xp(user1, xp_granted)
        #grant the user a random amount of coins between 10 and 20
        await db_manager.add_money(user1, coins_granted)
        #send a message to the channel saying the users xp and coins
        #convert the xp and coins to strings
        xp_granted = str(xp_granted)
        coins_granted = str(coins_granted)
        await ctx.send(user1_name + " has won the fight and has been granted " + coins_granted + " xp and " + coins_granted + " coins!")
        
        #check if the user has leveled up by checking if the users xp is greater than or equal to the xp needed to level up
        if await db_manager.can_level_up(user1):
            #if the user can level up, level them up
            await db_manager.add_level(user1, 1)
            #set the users xp to 0
            await db_manager.set_xp(user1, 0)
            #send a message to the channel saying the user has leveled up
            #get the users new level
            new_level = await db_manager.get_level(user1)
            await ctx.send(user1_name + " has leveled up! They are now level " + str(new_level) + "!")
            

        return user1
    else:
        print("User 2 won!")
        #set new description to the previous description plus the winner
        Newdescription = prev_desc + "\n" + "🏆" + user2_name + " won!"
        Newdescription = str(Newdescription)
        #if there are more than 4 lines in the embed, remove the first line
        if Newdescription.count("\n") >= 3:
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
        xp_granted = random.randint(10, 20)
        coins_granted = random.randint(10, 20)
        #grant the user a random amount of xp between 10 and 20
        await db_manager.add_xp(user2, xp_granted)
        #grant the user a random amount of coins between 10 and 20
        await db_manager.add_money(user2, coins_granted)
        #send a message to the channel saying the users xp and coins
        #convert the xp and coins to strings
        xp_granted = str(xp_granted)
        coins_granted = str(coins_granted)
        await ctx.send(user2_name + " has won the fight and has been granted " + coins_granted + " xp and " + coins_granted + " coins!")
        
        #check if the user has leveled up by checking if the users xp is greater than or equal to the xp needed to level up 
        if await db_manager.can_level_up(user2):
            #if the user can level up, level them up
            await db_manager.add_level(user2, 1)
            #set the users xp to 0
            await db_manager.set_xp(user2, 0)
            #send a message to the channel saying the user has leveled up
            #get the users new level
            new_level = await db_manager.get_level(user2)
            await ctx.send(user2_name + " has leveled up! They are now level " + str(new_level) + "!")
        return user2
    








#----------------------------------deathbattle_monster----------------------------------#
#a deathbattle between a user and a monster
async def deathbattle_monster(ctx: Context, userID, userName, monsterID, monsterName):
    #set the turn to 0
    turnCount = 0
    #create the embed and send it
    embed = discord.Embed(title="Deathbattle", description="Fight!", color=0xffff00)
    embed.add_field(name=userName, value="Health: 100", inline=True)
    embed.add_field(name=monsterName, value="Health: 100", inline=True)
    #set the user in combat
    await db_manager.set_in_combat(userID)
    msg = await ctx.send(embed=embed)
    #set the prev_desc to blank
    prev_desc = ""
    #while both the user and the monster are alive
    #get the health of the user
    user_health = await db_manager.get_health(userID)
    #get the health of the monster
    monster_health = await db_manager.get_enemy_health(monsterID)
    #convert the health to str
    user_health = str(user_health)
    monster_health = str(monster_health)
    user_burn_turn = None
    user_poison_turn = None
    user_paralyze_turn = None
    enemy_burn_turn = None
    enemy_poison_turn = None
    enemy_paralyze_turn = None
    
    #while the user and monster are alive
    while user_health != "0" and monster_health != "0":
        #users turn
        if turnCount % 2 == 0:
            #if its been two turns since the user was set on fire, remove the burning status
            if user_burn_turn != None and turnCount - user_burn_turn >= 2:
                user_burn_turn = None
                db_manager.set_user_not_burning(userID)

            #if its been 2 turns since the user was poisoned, remove the poisoned status
            if user_poison_turn != None and turnCount - user_poison_turn >= 2:
                user_poison_turn = None
                db_manager.set_user_not_poisoned(userID)

            #if its been 1 turn since the user was paralyzed, remove the paralyzed status
            if user_paralyze_turn != None and turnCount - user_paralyze_turn >= 1:
                user_paralyze_turn = None
                db_manager.set_user_not_paralyzed(userID)
                
            user1_weapon = await db_manager.get_equipped_weapon(userID)
            #print(user1_weapon)
            if user1_weapon == None or user1_weapon == []:
                user1_weapon_name = "Fists"
                user1_damage = 1
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
            user1_armor = await db_manager.get_equipped_armor(userID)
            if user1_armor == None or user1_armor == []:
                user1_armor_name = "Clothes"
                user1_defense = 1
            else:
                user1_armor_name = user1_armor[0][2]
                user1_defense = user1_armor[0][8]
                
            #get the monsters attack
            monster_attack = await db_manager.get_enemy_damage(monsterID)
            #monsters defence is half of their health
            monster_defence = await db_manager.get_enemy_health(monsterID)
            #convert the defence to int
            monster_defence = int(monster_defence[0])
            #divide the defence by 2
            monster_defence = monster_defence / 2
            
            #get the enemies name and convert it to str
            monster_name = await db_manager.get_enemy_name(monsterID)
            #get the users attack
            #calculate the damage
            damage = user1_damage - monster_defence
            #convert the damage to int
            damage = int(damage)
            #if the damage is less than 0, set it to 0
            if damage < 0:
                damage = 0
                
            #if the monsters defense is higher than the users attack, set the damage to 0, and say the monster blocked the attack
            if monster_defence > user1_damage:
                damage = 0
                #tell the user the monster is too powerful and they ran away
                await ctx.send("The monster is too powerful and you ran away!")
                #replace the embed description with "You ran away!"
                embed.description = "You ran away!"
                #set the embed color to red
                embed.color = 0xff0000
                #edit the embed
                await msg.edit(embed=embed)
                #set the user not in combat
                await db_manager.set_not_in_combat(userID)
                return None
        
            #if the damage is more than the monsters health, set the damage to the monsters health
            #convert the monsters health to int
            monster_health = str(monster_health).replace("(", "")
            monster_health = str(monster_health).replace(")", "")
            monster_health = str(monster_health).replace(",", "")
            #convert to int
            monster_health = int(monster_health)
            if damage > monster_health:
                damage = monster_health
            #remove the damage from the monsters health
            await db_manager.remove_enemy_health(monsterID, damage)
            
            if user1_weapon_subtype == "Fire" and isSetONFire == 1:
                Newdescription = prev_desc + "\n" + "__" + user1_name + "__ set __" + monster_name + "__ on fire <:flame1:1061287587395948634> __ for __" + str(monster_attack) + "__ plus 1 damage per turn (burning)"
                #set the users burn status to true
                await db_manager.set_enemy_burning(monsterID)
                #mark the turn the user was set on fire
                enemy_burn_turn = turnCount
                
            #if the user is poisoned, tell the user they were poisoned, skip their turn and add a (poisoned) to the end of the damage
            elif user1_weapon_subtype == "Poison" and isPoisoned == 1:
                Newdescription = prev_desc + "\n" + "__" + user1_name + "__ poisoned <:poisoned:1061287780652691466> __" + monster_name + "__ for __" + str(monster_attack) + "__ plus 3 damage per turn (poisoned)"
                #set the users poison status to true
                await db_manager.set_enemy_poisoned(monsterID)
                #mark the turn the user was poisoned
                enemy_poison_turn = turnCount

            #if the subtype is paralyze, tell the user they were paralyzed and skip their turn
            elif user1_weapon_subtype == "Paralyze" and isParalyzed == 1:
                Newdescription = prev_desc + "\n" + "__" + user1_name + "__ paralyzed <:paralyzed:1061287659722510419> __" + monster_name + "__ for __" + str(monster_attack) + "__ they wont be able to attack for a turn (paralyzed)"
                #set the users poison status to true
                await db_manager.set_enemy_paralyzed(monsterID)
                #mark the turn the user was poisoned
                enemy_paralyze_turn = turnCount
                #skip the users turn
                turnCount += 1
            
            #import the json of the user1Promts
            with open("assets/user_enemy_Promts.json") as f:
                user1Promts = json.load(f)
            #get a random user1 promt
            user1Promt = random.choice(user1Promts)
            #convert the promt to a string
            user1Promt = str(user1Promt)
            #replace the {user2_name} with the user2 name
            #convert both names to strings
            user1_name = str(userName)
            monster_name = str(monster_name)
            user1Promt = user1Promt.replace("{monster_name}", "__" + monster_name + "__")
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
            if Newdescription.count("\n") >= 3:
                Newdescription = Newdescription.split("\n", 1)[1]
            embed = discord.Embed(description=f"{Newdescription}", color=0xffff00)
            #edit the embed feilds to include the new health
            user1_health = await db_manager.get_health(userID)
            enemyHealth = await db_manager.get_enemy_health(monsterID)
            #remove the () and , from the health
            user1_health = str(user1_health).replace("(", "")
            user1_health = str(user1_health).replace(")", "")
            user1_health = str(user1_health).replace(",", "")
            enemyHealth = str(enemyHealth).replace("(", "")
            enemyHealth = str(enemyHealth).replace(")", "")
            enemyHealth = str(enemyHealth).replace(",", "")
            #convert to int
            user1_health = int(user1_health)
            enemyHealth = int(enemyHealth)
            #if the user is dead, set their health to 0
            if user1_health <= 0:
                user1_health = 0
            if enemyHealth <= 0:
                enemyHealth = 0

            #convert back to string
            user1_health = str(user1_health)
            enemyHealth = str(enemyHealth)
            
            if await db_manager.check_user_burning(userID):
                await db_manager.remove_health(userID, 1)
                #add a (burning) to the users health
                user1_health = user1_health + " (burning)"
                #mark down the turn count when the user was set on fire
                
            if await db_manager.check_enemy_burning(monsterID):
                await db_manager.remove_enemy_health(monsterID, 1)
                #add a (burning) to the users health
                monster_health = monster_health + " (burning)"
                #mark down the turn count when the user was set on fire

            if await db_manager.check_user_poisoned(userID):
                await db_manager.remove_health(userID, 3)
                #add a (poisoned) to the users health
                user1_health = user1_health + " (poisoned)"
                #mark down the turn count when the user was set on fire
            
            if await db_manager.check_enemy_poisoned(monsterID):
                await db_manager.remove_enemy_health(monsterID, 3)
                #add a (poisoned) to the users health
                monster_health = monster_health + " (poisoned)"
                #mark down the turn count when the user was set on fire
                
            if await db_manager.check_user_paralyzed(userID):
                user1_health = user1_health + " (paralyzed)"
            
            if await db_manager.check_enemy_paralyzed(monsterID):
                monster_health = monster_health + " (paralyzed)"
                
            embed = discord.Embed(description=f"{Newdescription}")
            #set the embed color to green
            embed.color = 0x00ff00
            embed.add_field(name=user1_name, value="Health: " + user1_health, inline=True)
            embed.add_field(name=monster_name, value="Health: " + enemyHealth, inline=True)
            prev_desc = Newdescription
            #Q, whats the hex color for green
            #A, 0x00ff00
            await msg.edit(embed=embed)

            #add 1 to the turn count
            #sleep for 2 seconds
            turnCount += 1
            await asyncio.sleep(2)
            
            #add 1 to the turn count
            #if the monster is dead, give the user xp and coins and end the fight
            #get the monsters health
            monster_health = await db_manager.get_enemy_health(monsterID)
            #convert the health to int
            monster_health = int(monster_health[0])
            #if the health is less than or equal to 0
            if monster_health <= 0:
                #get the users name
                #convert the name to str
                user1_name = str(userName)
                #get the enemies xp and coins to give to the user
                monster_xp = await db_manager.get_enemy_xp(monsterID)
                monster_coins = await db_manager.get_enemy_money(monsterID)
                
                #get the enemys drop and drop min and max 
                monster_drop = await db_manager.get_enemy_drop(monsterID)
                monster_drop_chance = await db_manager.get_enemy_drop_chance(monsterID)
                monster_drop_min = await db_manager.get_enemy_drop_amount_min(monsterID)
                monster_drop_max = await db_manager.get_enemy_drop_amount_max(monsterID)
                
                
                #convert the xp and coins to str
                monster_xp = str(monster_xp)
                monster_coins = str(monster_coins)
                #remove the () and , from the xp and coins
                monster_xp = monster_xp.replace("(", "")
                monster_xp = monster_xp.replace(")", "")
                monster_xp = monster_xp.replace(",", "")
                monster_coins = monster_coins.replace("(", "")
                monster_coins = monster_coins.replace(")", "")
                monster_coins = monster_coins.replace(",", "")
                #convert the xp and coins to str
                monster_xp = str(monster_xp)
                monster_coins = str(monster_coins)
                #send a message to the channel saying the users xp and coins
                await ctx.send(user1_name + " has won the fight and has been granted " + monster_xp + " xp and " + monster_coins + " coins!")
                #check if the user has leveled up by checking if the users xp is greater than or equal to the xp needed to level up 
                #reconvert them back to int
                monster_xp = int(monster_xp)
                monster_coins = int(monster_coins)
                #give the user their xp and coins
                await db_manager.add_xp(userID, monster_xp)
                await db_manager.add_money(userID, monster_coins)
                
                #get the users quest 
                quest_id = await db_manager.get_user_quest(userID)
                objective = await db_manager.get_quest_objective_from_id(quest_id)
                quest_type = await db_manager.get_quest_type(quest_id)
                #if the quest type is kill
                if quest_type == "kill":
                    #get the string of the monster name from the objective 
                    objective = objective.split(" ")
                    objective = objective[1]
                    #if the objective is the same as the monster id
                    if objective == monsterID:
                        #add 1 to the quest progress
                        await db_manager.update_quest_progress(userID, quest_id, 1)
                        #get the quest progress
                        quest_progress = await db_manager.get_quest_progress(userID)
                        #get the quest total
                        quest_total = await db_manager.get_quest_total_from_id(quest_id)
                        #if the quest progress is greater than or equal to the quest total
                        if quest_progress >= quest_total:
                            #get the quest reward type and amount
                            quest_reward_type = await db_manager.get_quest_reward_type_from_id(quest_id)
                            quest_reward_amount = await db_manager.get_quest_reward_amount_from_id(quest_id)
                            quest_xp_reward = await db_manager.get_quest_xp_reward_from_id(quest_id)
                            #add the quest xp reward to the users xp
                            await db_manager.add_xp(userID, quest_xp_reward)
                            #if the quest reward type is gold, add the amount to the users gold
                            if quest_reward_type == "gold":
                                await db_manager.add_money(userID, quest_reward_amount)
                                await ctx.send(f"You have completed the quest and been rewarded with {quest_reward_amount} gold!, and {quest_xp_reward} xp!")
                            #if the quest reward type is item get all the info on the item and add it to the users inventory
                            elif quest_reward_type == "item":
                                #get all the info on the item
                                item_name = await db_manager.get_basic_item_name(quest_reward_amount)
                                item_price = await db_manager.get_basic_item_price(quest_reward_amount)
                                item_type = await db_manager.get_basic_item_type(quest_reward_amount)
                                item_emoji = await db_manager.get_basic_item_emote(quest_reward_amount)
                                item_rarity = await db_manager.get_basic_item_rarity(quest_reward_amount)
                                item_damage = await db_manager.get_basic_item_damage(quest_reward_amount)
                                item_sub_type = await db_manager.get_basic_item_sub_type(quest_reward_amount)
                                item_crit_chance = await db_manager.get_basic_item_crit_chance(quest_reward_amount)
                                item_projectile = await db_manager.get_basic_item_projectile(quest_reward_amount)
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
                                item_sub_type = str(item_sub_type[0])
                                #convert the item crit chance to int
                                item_crit_chance = int(item_crit_chance[0])
                                #convert the item projectile to str
                                item_projectile = str(item_projectile[0])
                                #add the item to the users inventory, with all the info needed for the function
                                await db_manager.add_item_to_inventory(userID, item_name, item_price, item_type, item_emoji, item_rarity, 1, item_type, item_damage, False, item_sub_type, item_crit_chance, item_projectile)
                                await ctx.send(f"You have completed the quest and been rewarded with {item_name}!, and {quest_xp_reward} xp!")
                            #mark the quest as complete
                            await db_manager.mark_quest_completed(userID, quest_id)
                #get all the info on the drop item
                item_name = await db_manager.get_basic_item_name(monster_drop)
                item_price = await db_manager.get_basic_item_price(monster_drop)
                item_type = await db_manager.get_basic_item_type(monster_drop)
                item_emoji = await db_manager.get_basic_item_emote(monster_drop)
                item_rarity = await db_manager.get_basic_item_rarity(monster_drop)
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
                
                
                #calculate the how many items the user will get
                #get the drop chance
                monster_drop_chance = int(monster_drop_chance[0])
                #get the drop min and max
                monster_drop_min = int(monster_drop_min[0])
                monster_drop_max = int(monster_drop_max[0])
                #get a random number between the min and max
                drop_amount = random.randint(monster_drop_min, monster_drop_max)
                #get a random number between 1 and 100
                drop_chance = random.randint(1, 100)
                #if the drop chance is less than or equal to the monsters drop chance
                if drop_chance <= monster_drop_chance:
                    #give the user the drop
                    await db_manager.add_item_to_inventory(userID, monster_drop, item_name, item_price, item_emoji, item_rarity, drop_amount, item_type, 0, False, "None", "0", "None")
                    #send a message to the channel saying the user got the drop
                    await ctx.send(user1_name + " has gotten " + str(drop_amount) + " " + monster_drop + "!")
                if await db_manager.can_level_up(userID):
                    #if the user can level up, level them up
                    await db_manager.add_level(userID, 1)
                    #set the users xp to 0
                    await db_manager.set_xp(userID, 0)
                    #send a message to the channel saying the user has leveled up
                    #get the users new level
                    new_level = await db_manager.get_level(userID)
                    #remove the () and , from the level
                    new_level = str(new_level)
                    new_level = new_level.replace("(", "")
                    new_level = new_level.replace(")", "")
                    new_level = new_level.replace(",", "")
                    #convert the level to int
                    new_level = int(new_level)
                    await ctx.send(user1_name + " has leveled up! They are now level " + str(new_level) + "!")
                return userID
        #monsters turn to attack
        if turnCount % 2 == 1:
        #if its been two turns since the user was set on fire, remove the burning status
            if enemy_burn_turn != None and turnCount - enemy_burn_turn >= 2:
                enemy_burn_turn = None
                db_manager.set_enemy_not_burning(monsterID)

            #if its been 2 turns since the user was poisoned, remove the poisoned status
            if enemy_poison_turn != None and turnCount - enemy_poison_turn >= 2:
                enemy_poison_turn = None
                db_manager.set_enemy_not_poisoned(monsterID)

            #if its been 1 turn since the user was paralyzed, remove the paralyzed status
            if enemy_paralyze_turn != None and turnCount - enemy_paralyze_turn >= 1:
                enemy_paralyze_turn = None
                db_manager.set_enemy_not_paralyzed(monsterID)
                
            #if the enemy is on fire, deal 3 damage to them
            isBurning = await db_manager.check_enemy_burning(monsterID)
            if isBurning:
                await db_manager.remove_enemy_health(monsterID, 3)
                
            #if the enemy is poisoned, deal 1 damage to them
            isPoisoned = await db_manager.check_enemy_poisoned(monsterID)
            if isPoisoned:
                await db_manager.remove_enemy_health(monsterID, 1)
                
            #get the monsters attack
            monster_attack = await db_manager.get_enemy_damage(monsterID)
            #convert the attack to int
            monster_attack = int(monster_attack[0])
            #monsters defence is half of their health
            monster_defence = await db_manager.get_enemy_health(monsterID)
            #convert the defence to int
            monster_defence = int(monster_defence[0])
            #divide the defence by 2
            monster_defence = monster_defence / 2
            
            #get the users armor
            user1_armor = await db_manager.get_equipped_armor(userID)
            if user1_armor == None or user1_armor == []:
                user1_armor_name = "Clothes"
                user1_defense = 1
            else:
                user1_armor_name = user1_armor[0][2]
                user1_defense = user1_armor[0][8]
                #convert the defense to int
                user1_defense = int(user1_defense)
            #get the users equipped weapon
            user1_weapon = await db_manager.get_equipped_weapon(userID)
            if user1_weapon == None or user1_weapon == []:
                user1_weapon_name = "Fists"
                user1_damage = 1
            else:
                user1_weapon_name = user1_weapon[0][2]
                user1_damage = user1_weapon[0][8]
            #get the users name and convert it to str
            
            user1_name = str(user1_name)
            #calculate the damage
            damage = monster_attack - user1_defense
            isSetONFire = random.randint(1, 10)
            #have the user have a 1/10 chance of being paralyzed
            isPoisoned = random.randint(1, 10)
            #a 1/10 chance of being paralyzed
            isParalyzed = random.randint(1, 10)
            #if the sub type is Fire tell the user they were set on fire and add a (burning) to the end of the damage
            monster_element = await db_manager.get_enemy_element(monsterID)
            if monster_element == "Fire" and isSetONFire == 1:
                Newdescription = prev_desc + "\n" + "__" + monster_name + "__ set __" + user1_name + "__ on fire <:flame1:1061287587395948634> __ for __" + str(monster_attack) + "__ plus 1 damage per turn (burning)"
                #set the users burn status to true
                await db_manager.set_user_burning(userID)
                #mark the turn the user was set on fire
                user_burn_turn = turnCount
                
            #if the user is poisoned, tell the user they were poisoned, skip their turn and add a (poisoned) to the end of the damage
            elif monster_element == "Poison" and isPoisoned == 1:
                Newdescription = prev_desc + "\n" + "__" + monster_name + "__ poisoned <:poisoned:1061287780652691466> __" + user1_name + "__ for __" + str(monster_attack) + "__ plus 3 damage per turn (poisoned)"
                #set the users poison status to true
                await db_manager.set_user_poisoned(userID)
                #mark the turn the user was poisoned
                user_poison_turn = turnCount

            #if the subtype is paralyze, tell the user they were paralyzed and skip their turn
            elif monster_element == "Paralyze" and isParalyzed == 1:
                Newdescription = prev_desc + "\n" + "__" + monster_name + "__ paralyzed <:paralyzed:1061287659722510419> __" + user1_name + "__ for __" + str(monster_attack) + "__ they wont be able to attack for a turn (paralyzed)"
                #set the users poison status to true
                await db_manager.set_user_paralyzed(userID)
                #mark the turn the user was poisoned
                user_paralyze_turn = turnCount
                #skip the users turn
                turnCount += 1

            #get the crit chance of the monster
            monster_crit_chance = await db_manager.get_enemy_crit_chance(monsterID)
            #remove the % from the crit chance
            #get the monsters element

            
            #convert the crit chance to int
            monster_crit_chance = int(monster_crit_chance[0])
            #get a random number between 1 and 100
            crit_chance = random.randint(1, 100)
            #if the crit chance is less than or equal to the monsters crit chance
            if crit_chance <= monster_crit_chance:
                #double the damage
                damage = damage * 2
                #set newdriscription to the crit message
                Newdescription = "__" + monster_name + "__ has crit __" + user1_name + "__ for __" + str(damage) + "__ damage!"  
            #if the damage is less than 0, set it to 0
            if damage < 0:
                damage = 0
            #if the monsters attack is less than the users defense, set the damage to 0
            if monster_attack < user1_defense:
                damage = 0
            #if the damage is greater than the users health, set the damage to the users health
            if damage > user1_health:
                damage = user1_health
            #remove the damage from the users health
            await db_manager.remove_health(userID, damage)
            
            #import the json of the enemyPromts
            with open("assets/enemy_user_Promts.json") as f:
                enemyPromts = json.load(f)
            #get a random user2 promt
            enemyPromts = random.choice(enemyPromts)
            #convert the promt to a string
            enemyPromts = str(enemyPromts)
            #replace the {user2_name} with the user2 name
            #convert both names to strings
            monster_name = str(monster_name)
            enemyPromts = enemyPromts.replace("{monster_name}", "__" + monster_name + "__")
            #replace {user1_name} with the user1 name
            enemyPromts = enemyPromts.replace("{user1_name}", "__" + user1_name + "__")
            #replace {monster_damage} with the monster damage
            enemyPromts = enemyPromts.replace("{monster_damage}", "__" + str(monster_attack) + "__")
            Newdescription = prev_desc + "\n" + f"{enemyPromts}"
            #convert the embed to a string
            Newdescription = str(Newdescription)
            #if there are more than 4 lines in the embed, remove the first line
            if Newdescription.count("\n") >= 3:
                Newdescription = Newdescription.split("\n", 1)[1]
            embed = discord.Embed(description=f"{Newdescription}", color=0xffff00)
            #edit the embed feilds to include the new health
            user1_health = await db_manager.get_health(userID)
            enemyHealth = await db_manager.get_enemy_health(monsterID)
            #remove the () and , from the health
            user1_health = str(user1_health).replace("(", "")
            user1_health = str(user1_health).replace(")", "")
            user1_health = str(user1_health).replace(",", "")
            enemyHealth = str(enemyHealth).replace("(", "")
            enemyHealth = str(enemyHealth).replace(")", "")
            enemyHealth = str(enemyHealth).replace(",", "")
            #convert to int
            user1_health = int(user1_health)
            enemyHealth = int(enemyHealth)
            
            #if the user is dead, set their health to 0
            if user1_health <= 0:
                user1_health = 0
            if enemyHealth <= 0:
                enemyHealth = 0

            #convert back to string
            user1_health = str(user1_health)
            enemyHealth = str(enemyHealth)
            
            if await db_manager.check_user_burning(userID):
                await db_manager.remove_health(userID, 1)
                #add a (burning) to the users health
                user1_health = user1_health + " (burning)"
                #mark down the turn count when the user was set on fire
                
            if await db_manager.check_enemy_burning(monsterID):
                await db_manager.remove_enemy_health(monsterID, 1)
                #add a (burning) to the users health
                monster_health = monster_health + " (burning)"
                #mark down the turn count when the user was set on fire

            if await db_manager.check_user_poisoned(userID):
                await db_manager.remove_health(userID, 3)
                #add a (poisoned) to the users health
                user1_health = user1_health + " (poisoned)"
                #mark down the turn count when the user was set on fire
            
            if await db_manager.check_enemy_poisoned(monsterID):
                await db_manager.remove_enemy_health(monsterID, 3)
                #add a (poisoned) to the users health
                monster_health = monster_health + " (poisoned)"
                #mark down the turn count when the user was set on fire
                
            if await db_manager.check_user_paralyzed(userID):
                user1_health = user1_health + " (paralyzed)"
            
            if await db_manager.check_enemy_paralyzed(monsterID):
                monster_health = monster_health + " (paralyzed)"
                
            embed = discord.Embed(description=f"{Newdescription}")
            #set the embed color to red
            embed.color = 0xff0000
            embed.add_field(name=user1_name, value="Health: " + user1_health, inline=True)
            embed.add_field(name=monster_name, value="Health: " + enemyHealth, inline=True)
            prev_desc = Newdescription
            #Q, whats the hex color for green
            #A, 0x00ff00
            await msg.edit(embed=embed)

            #add 1 to the turn count
            #sleep for 2 seconds
            turnCount += 1
            await asyncio.sleep(2)
            #send a message to the channel saying the damage done
            #add 1 to the turn count
            #if the user is dead, end the fight
            #get the users health
            
            userHealth = await db_manager.get_health(userID)
            #convert it to int 
            userHealth = int(userHealth[0])
            #if the users health is less than or equal to 0, end the fight
            if userHealth <= 0:
                #get the monsters name
                #convert the name to str
                monster_name = str(monster_name)
                #send a message to the channel saying the user has died
                await ctx.send(user1_name + " has died!")
                #set the users health to 0
                await db_manager.set_health(userID, 0)
                #set the user as dead 
                await db_manager.set_dead(userID)
                #set the user not in combat
                await db_manager.set_not_in_combat(userID)
                return userID
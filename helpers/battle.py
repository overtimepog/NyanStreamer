import asyncio
import json
import os
import random
from io import BytesIO
import re
from typing import Any, Optional, Tuple, Union

import aiohttp
import aiosqlite
import discord
import requests
from discord.ext import commands
from discord.ext.commands import Bot, Context
from PIL import Image, ImageChops, ImageDraw, ImageFont

from helpers import db_manager

#-------------------Death Battle-------------------#
async def deathbattle(ctx: Context, user1, user2, user1_name, user2_name):
    turnCount = 0
    #set each users isInCombat to true
    #DONE: figure out how to get the path of this file without hardcoding it
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
    msg = await ctx.channel.send(embed=embed)
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
            user1_damage = random.randint(1, 10)
            user1_weapon_subtype = "None"
            #convert subtype to str
            user1_weapon_subtype = str(user1_weapon_subtype)
            #convert projectile to str
        else:
            user1_weapon_name = user1_weapon[0][2]
            #convert it to str
            user1_weapon_name = str(user1_weapon_name)
            user1_damage = user1_weapon[0][8]
            user1_damage = str(user1_damage)
            #split it by the - 
            user1_damage = user1_damage.split("-")
            #get a random number between the two numbers
            user1_damage = random.randint(int(user1_damage[0]), int(user1_damage[1]))
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
            #the damage is any number between 1 and 10
            user2_damage = random.randint(1, 10)
            user2_weapon_subtype = "None"
            #convert subtype to str
            user2_weapon_subtype = str(user2_weapon_subtype)
        else:
            user2_weapon_name = user2_weapon[0][2]
            #convert it to str
            user2_weapon_name = str(user2_weapon_name)
            user2_damage = user2_weapon[0][8]
            user2_damage = str(user2_damage)
            #split it by the - 
            user2_damage = user2_damage.split("-")
            #get a random number between the two numbers
            user2_damage = random.randint(int(user2_damage[0]), int(user2_damage[1]))
            user2_weapon_subtype = user2_weapon[0][10]
            #convert subtype to str
            user2_weapon_subtype = str(user2_weapon_subtype)
            #if the users weapon has the item_projectile arrow, make sure the user has arrows
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
        #TODO: add the crit chance stat to this calculation
        user1_weapon_crit = int(user1_crit)
        user2_weapon_crit = int(user2_crit)
        user1_crit_stat = await db_manager.get_crit_chance(user1)
        user2_crit_stat = await db_manager.get_crit_chance(user2)
        user1_crit = user1_weapon_crit + user1_crit_stat
        user2_crit = user2_weapon_crit + user2_crit_stat
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
                await db_manager.set_user_not_burning(user1)

            #if its been 2 turns since the user was poisoned, remove the poisoned status
            if user1_poison_turn != None and turnCount - user1_poison_turn >= 2:
                user1_poison_turn = None
                await db_manager.set_user_not_poisoned(user1)

            #if its been 1 turn since the user was paralyzed, remove the paralyzed status
            if user1_paralyze_turn != None and turnCount - user1_paralyze_turn >= 1:
                user1_paralyze_turn = None
                await db_manager.set_user_not_paralyzed(user1)
    
            #user 1 attacks
            
            #if the user is using a projectile weapon, remove an arrow
            await db_manager.remove_health(user2, user1_damage)
            #have the user have a 1/10 chance of being set on fire
            #TODO: add the imunity stat to this calculation
            user2_fire_resistance = await db_manager.get_fire_resistance(user2)
            user2_paralyze_resistance = await db_manager.get_paralysis_resistance(user2)
            user2_poison_resistance = await db_manager.get_poison_resistance(user2)
            
            isSetONFire = random.randint(1, 10)
            #if the fire resistance / 10 is greater than the number, the user is immune to fire
            if user2_fire_resistance / 10 >= isSetONFire:
                isSetONFire = 0
            
            #have the user have a 1/10 chance of being poisoned
            #if the poison resistance / 10 is greater than the number, the user is immune to poison
            isPoisoned = random.randint(1, 10)
            if user2_poison_resistance / 10 >= isPoisoned:
                isPoisoned = 0
            #a 1/10 chance of being paralyzed
            isParalyzed = random.randint(1, 10)
            #if the paralysis resistance / 10 is greater than the number, the user is immune to paralysis
            if user2_paralyze_resistance / 10 >= isParalyzed:
                isParalyzed = 0
            #make embed with the previous description plus the new description
            if prev_desc == None:
                prev_desc = ""
                
            user1_weapon = await db_manager.get_item_id(user1_weapon_name)
            if user1_weapon == None:
                user_weapon_quotes = [
                    "{user} trips and accidentally hurls a rock, it bounces off a wall and hits {target} for {damage} damage. Accurate and hilarious!",
                    "{user} digs in their pockets and pulls out a stale loaf of bread, hurling it at {target}. It hits for {damage} damage. Who knew carbs could be so dangerous?",
                    "{user} fumbles around and finds an old boot, flings it with surprising accuracy at {target} causing {damage} damage. A boot to the face, now that's got to hurt!",
                    "{user} inexplicably starts a dance-off. The unexpected and horrific dance moves confuse {target}, causing {damage} damage. That's one way to use the power of dance!",
                    "{user} finds a squeaky toy in their pocket and throws it at {target}. It hits for {damage} damage. Who's a good boy now, huh?",
                    "{user} pulls out a feather and tickles {target}. It's so ticklish that it takes {damage} damage. Laughter really is the best... weapon?",
                    "{user} summons a horde of angry pigeons that swoop down on {target}, causing {damage} damage. They've really got those birds trained!",
                    "{user} pulls out a rubber chicken and slaps {target} around a bit with it. It's so absurd that it causes {damage} damage. If you can't beat 'em, make 'em laugh!",
                    "{user} starts telling a bad joke. {target} laughs so hard they take {damage} damage. A sense of humor can be a lethal weapon!",
                    "{user} pulls out a spoon and charges at {target}. It's so unexpected that it causes {damage} damage. Never underestimate the power of cutlery!"
                ]
            else:
                user_weapon_quotes = await db_manager.get_item_quotes(user1_weapon)
            user1Promt = random.choice(user_weapon_quotes)
            if user1Promt == user1_weapon:
                user1Promt = random.choice(user_weapon_quotes)
            user1Promt = str(user1Promt)
            user1Promt = user1Promt.replace("{user}", user1_name)
            user1Promt = user1Promt.replace("{target}", user2_name)
            user1Promt = user1Promt.replace("{damage}", str(user1_damage))
            desc = prev_desc + "\n" + f"{user1Promt}"
            #if they crit, add a (crit) to the end of the damage
            if user1_roll <= user1_crit:
                Newdescription = desc + "and hit a Critical Hit!"
            #if the sub type is Fire tell the user they were set on fire and add a (burning) to the end of the damage
            elif user1_weapon_subtype == "Fire" and isSetONFire == 1:
                Newdescription = desc + "and Set them on Fire"
                #set the users burn status to true
                await db_manager.set_user_burning(user2)
                #mark the turn the user was set on fire
                user2_burn_turn = turnCount
                
            #if the user is poisoned, tell the user they were poisoned, skip their turn and add a (poisoned) to the end of the damage
            elif user1_weapon_subtype == "Poison" and isPoisoned == 1:
                Newdescription = desc + "and Poisoned them"
                #set the users poison status to true
                await db_manager.set_user_poisoned(user2)
                #mark the turn the user was poisoned
                user2_poison_turn = turnCount

            #if the subtype is paralyze, tell the user they were paralyzed and skip their turn
            elif user1_weapon_subtype == "Paralyze" and isParalyzed == 1:
                Newdescription = desc + "and Paralyzed them"
                #set the users poison status to true
                await db_manager.set_user_paralyzed(user2)
                #mark the turn the user was poisoned
                user2_paralyze_turn = turnCount
                #skip the users turn
                turnCount += 1
            else:
                Newdescription = desc
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
        #STUB - USER 2's TURN
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
            user1_fire_resistance = await db_manager.get_fire_resistance(user1)
            user1_paralyze_resistance = await db_manager.get_paralysis_resistance(user1)
            user1_poison_resistance = await db_manager.get_poison_resistance(user1)
            
            isSetONFire = random.randint(1, 10)
            #if the fire resistance / 10 is greater than the number, the user is immune to fire
            if user1_fire_resistance / 10 >= isSetONFire:
                isSetONFire = 0
            
            #have the user have a 1/10 chance of being poisoned
            #if the poison resistance / 10 is greater than the number, the user is immune to poison
            isPoisoned = random.randint(1, 10)
            if user1_poison_resistance / 10 >= isPoisoned:
                isPoisoned = 0
                
            #a 1/10 chance of being paralyzed
            isParalyzed = random.randint(1, 10)
            #if the paralysis resistance / 10 is greater than the number, the user is immune to paralysis
            if user1_paralyze_resistance / 10 >= isParalyzed:
                isParalyzed = 0

            #make embed with the previous description plus the new description
            if prev_desc == None:
                prev_desc = ""
            user2_weapon = await db_manager.get_item_id(user2_weapon_name)
            if user2_weapon == None:
                user_weapon_quotes = [
                    "{user} trips and accidentally hurls a rock, it bounces off a wall and hits {target} for {damage} damage. Accurate and hilarious!",
                    "{user} digs in their pockets and pulls out a stale loaf of bread, hurling it at {target}. It hits for {damage} damage. Who knew carbs could be so dangerous?",
                    "{user} fumbles around and finds an old boot, flings it with surprising accuracy at {target} causing {damage} damage. A boot to the face, now that's got to hurt!",
                    "{user} inexplicably starts a dance-off. The unexpected and horrific dance moves confuse {target}, causing {damage} damage. That's one way to use the power of dance!",
                    "{user} finds a squeaky toy in their pocket and throws it at {target}. It hits for {damage} damage. Who's a good boy now, huh?",
                    "{user} pulls out a feather and tickles {target}. It's so ticklish that it takes {damage} damage. Laughter really is the best... weapon?",
                    "{user} summons a horde of angry pigeons that swoop down on {target}, causing {damage} damage. They've really got those birds trained!",
                    "{user} pulls out a rubber chicken and slaps {target} around a bit with it. It's so absurd that it causes {damage} damage. If you can't beat 'em, make 'em laugh!",
                    "{user} starts telling a bad joke. {target} laughs so hard they take {damage} damage. A sense of humor can be a lethal weapon!",
                    "{user} pulls out a spoon and charges at {target}. It's so unexpected that it causes {damage} damage. Never underestimate the power of cutlery!"
                ]
            else:
                user_weapon_quotes = await db_manager.get_item_quotes(user2_weapon)
            user2Promt = random.choice(user_weapon_quotes)
            if user2Promt == user2_weapon:
                user2Promt = random.choice(user_weapon_quotes)
            user2Promt = str(user2Promt)
            user2Promt = user2Promt.replace("{user}", user2_name)
            user2Promt = user2Promt.replace("{target}", user1_name)
            user2Promt = user2Promt.replace("{damage}", str(user2_damage))
            desc = prev_desc + "\n" + f"{user2Promt}"
            #if they crit, add a (crit) to the end of the damage
            if user2_roll <= user2_crit:
                Newdescription = desc + "and hit a Critical Hit!"
            #if the sub type is Fire tell the user they were set on fire and add a (burning) to the end of the damage
            elif user2_weapon_subtype == "Fire" and isSetONFire == 1:
                Newdescription = desc + "and Set them on Fire"
                #set the users burn status to true
                await db_manager.set_user_burning(user1)
                #mark down the turn count when the user was set on fire
                user1_burn_turn = turnCount
            #if the sub type is Poison tell the user they were set on fire and add a (poisoned) to the end of the damage

            elif user2_weapon_subtype == "Poison" and isPoisoned == 1:
                Newdescription = desc + "and Poisoned them"
                #set the users poison status to true
                await db_manager.set_user_poisoned(user1)
                #mark down the turn count when the user was set on fire
                user1_poison_turn = turnCount
                
            #if the sub type is paralysis tell the user they were set on paralyzed and add a (paralyzed) to the end of the damage
            elif user2_weapon_subtype == "Paralysis" and isParalyzed == 1:
                #set the users paralysis status to true
                Newdescription = desc + "and Paralyzed them"
                await db_manager.set_user_paralyzed(user1)
                #skip the users turn
                #save the turn count when the user was paralyzed
                user1_paralyze_turn = turnCount
                turnCount = turnCount + 1
            else:
                Newdescription = desc
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

    #TODO - add the stats to the winning user
    if await db_manager.is_alive(user1):
        #once a user wins, set both users isInCombat to false, and edit the embed to show who won
        print("User 1 won!")
        await db_manager.add_battles_fought(user1, 1)
        await db_manager.add_battles_won(user1, 1)
        await db_manager.add_battles_fought(user2, 1)
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
        coins_granted = await db_manager.get_money(user2)
        coins_granted = coins_granted / 2
        coins_granted = int(coins_granted)
        #grant the user a random amount of xp between 10 and 20
        await db_manager.add_xp(user1, xp_granted)
        await db_manager.remove_money(user2, coins_granted)
        await db_manager.add_money(user1, coins_granted)
        #send a message to the channel saying the users xp and coins
        #convert the xp and coins to strings
        xp_granted = str(xp_granted)
        coins_granted = str(coins_granted)
        await ctx.send(user1_name + " has won the fight and has been granted " + xp_granted + " xp and " + coins_granted + f" coins! from {user2_name}")
        
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
        await db_manager.add_battles_fought(user2, 1)
        await db_manager.add_battles_won(user2, 1)
        await db_manager.add_battles_fought(user1, 1)
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
        coins_granted = await db_manager.get_money(user1)
        coins_granted = coins_granted / 2
        coins_granted = int(coins_granted)
        #grant the user a random amount of xp between 10 and 20
        await db_manager.add_xp(user2, xp_granted)
        #grant the user a random amount of coins between 10 and 20
        await db_manager.remove_money(user1, coins_granted)
        await db_manager.add_money(user2, coins_granted)
        #send a message to the channel saying the users xp and coins
        #convert the xp and coins to strings
        xp_granted = str(xp_granted)
        coins_granted = str(coins_granted)
        await ctx.send(user2_name + " has won the fight and has been granted " + xp_granted + " xp and " + coins_granted + f" coins! from {user1_name}")
        
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
    embed.add_field(name=userName, value="Ready", inline=True)
    embed.add_field(name=monsterName, value="Ready", inline=True)
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
                user1_damage = str(user1_damage)
                #split the user1_damage by the - 
                user1_damage = user1_damage.split("-")
                #get a random number between the two numbers
                user1_damage = random.randint(int(user1_damage[0]), int(user1_damage[1]))
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
            #divide the defence by 5
            monster_defence = monster_defence / 5
            #convert the defence to int
            monster_defence = int(monster_defence)
            
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
                await ctx.send("You are too weak to damage this monster, fleeing is the only option!")
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
            isSetONFire = random.randint(1, 10)
            #have the user have a 1/10 chance of being paralyzed
            isPoisoned = random.randint(1, 10)
            #a 1/10 chance of being paralyzed
            isParalyzed = random.randint(1, 10)
            monster_health = int(monster_health)
            if damage > monster_health:
                damage = monster_health
            #remove the damage from the monsters health
            monster_health = monster_health - damage
            
            if user1_weapon_subtype == "Fire" and isSetONFire == 1:
                Newdescription = prev_desc + "and set them on Fire"
                #set the users burn status to true
                await db_manager.set_enemy_burning(monsterID)
                #mark the turn the user was set on fire
                enemy_burn_turn = turnCount
                
            #if the user is poisoned, tell the user they were poisoned, skip their turn and add a (poisoned) to the end of the damage
            elif user1_weapon_subtype == "Poison" and isPoisoned == 1:
                Newdescription = prev_desc + "and Poisoned them"
                #set the users poison status to true
                await db_manager.set_enemy_poisoned(monsterID)
                #mark the turn the user was poisoned
                enemy_poison_turn = turnCount

            #if the subtype is paralyze, tell the user they were paralyzed and skip their turn
            elif user1_weapon_subtype == "Paralyze" and isParalyzed == 1:
                Newdescription = prev_desc + "and Paralyzed them"
                #set the users poison status to true
                await db_manager.set_enemy_paralyzed(monsterID)
                #mark the turn the user was poisoned
                enemy_paralyze_turn = turnCount
                #skip the users turn
                turnCount += 1
            user1_weapon = await db_manager.get_item_id(user1_weapon_name)
            user_weapon_quotes = await db_manager.get_item_quotes(user1_weapon)
            if user_weapon_quotes == None or user_weapon_quotes == [] or user_weapon_quotes == "" or user_weapon_quotes == "None":
                userPromt = "{user} attacked {target} for {damage} damage"
                userPromt = userPromt.replace("{user}", userName)
                userPromt = userPromt.replace("{target}", monsterName)
                userPromt = userPromt.replace("{damage}", str(damage))
            else:
                userPromt = random.choice(user_weapon_quotes)
                if userPromt == user1_weapon:
                    userPromt = "{user} attacked {target} for {damage} damage"
                    userPromt = str(userPromt)
                    userPromt = userPromt.replace("{user}", userName)
                    userPromt = userPromt.replace("{target}", monsterName)
                    userPromt = userPromt.replace("{damage}", str(damage))
                else:
                    userPromt = str(userPromt)
                    userPromt = userPromt.replace("{user}", userName)
                    userPromt = userPromt.replace("{target}", monsterName)
                    userPromt = userPromt.replace("{damage}", str(damage))

                #roll for a critical hit
            criticalHit = await db_manager.get_crit_chance(userID)
            #convert the critical hit to int
            criticalHit = int(criticalHit)
            #roll for a critical hit
            criticalHitRoll = random.randint(1, 100)
            #if the critical hit roll is less than or equal to the critical hit chance, double the damage
            if criticalHitRoll <= criticalHit:
                damage = damage * 2
                userPromt = userPromt + f" and hit a Crit !"

            Newdescription = prev_desc + "\n" + f"{userPromt}"
            #convert the embed to a string
            Newdescription = str(Newdescription)
            #if there are more than 4 lines in the embed, remove the first line
            if Newdescription.count("\n") >= 3:
                Newdescription = Newdescription.split("\n", 1)[1]
            embed = discord.Embed(description=f"{Newdescription}", color=0xffff00)
            #edit the embed feilds to include the new health
            user1_health = await db_manager.get_health(userID)
            #remove the () and , from the health
            user1_health = str(user1_health).replace("(", "")
            user1_health = str(user1_health).replace(")", "")
            user1_health = str(user1_health).replace(",", "")
            monster_health = str(monster_health).replace("(", "")
            monster_health = str(monster_health).replace(")", "")
            monster_health = str(monster_health).replace(",", "")
            #convert to int
            user1_health = int(user1_health)
            monster_health = int(monster_health)
            #if the user is dead, set their health to 0
            if user1_health <= 0:
                user1_health = 0
            if monster_health <= 0:
                monster_health = 0

            #convert back to string
            user1_health = str(user1_health)
            monster_health = str(monster_health)
            
            if await db_manager.check_user_burning(userID):
                await db_manager.remove_health(userID, 1)
                #add a (burning) to the users health
                user1_health = user1_health + " (burning)"
                #mark down the turn count when the user was set on fire
                
            if await db_manager.check_enemy_burning(monsterID):
                #remove 1 health from the monsters health
                monster_health = monster_health - 1
                #add a (burning) to the users health
                monster_health = monster_health + " (burning)"
                #mark down the turn count when the user was set on fire

            if await db_manager.check_user_poisoned(userID):
                await db_manager.remove_health(userID, 3)
                #add a (poisoned) to the users health
                user1_health = user1_health + " (poisoned)"
                #mark down the turn count when the user was set on fire
            
            if await db_manager.check_enemy_poisoned(monsterID):
                monster_health = monster_health - 3
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
            embed.add_field(name=userName, value="Health: " + user1_health, inline=True)
            monster_health = str(monster_health)
            embed.add_field(name=monster_name, value="Health: " + monster_health, inline=True)
            monster_health = int(monster_health)
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
            #if the health is less than or equal to 0
            monster_health = int(monster_health)
            if monster_health <= 0:
                #get the users name
                #convert the name to str
                userName = str(userName)
                #get the enemies xp and coins to give to the user
                monster_xp = await db_manager.get_enemy_xp(monsterID)
                monster_coins = await db_manager.get_enemy_money(monsterID)
                
                #get the enemys drop and drop min and max 
                
                #TODO: Change this to fit the new system
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
                embed = discord.Embed(description=f"{userName} has defeated {monster_name} and gained {monster_xp} xp and {monster_coins} coins")
                #set the embed color to green
                embed.color = 0x00ff00
                embed.add_field(name=userName, value="Health: " + user1_health, inline=True)
                monster_health = str(monster_health)
                embed.add_field(name=monster_name, value="Health: " + monster_health, inline=True)
                monster_health = int(monster_health)
                #Q, whats the hex color for green
                #A, 0x00ff00
                await msg.edit(embed=embed)
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
                            #get the quest reward from the quest id
                            quest_reward = await db_manager.get_quest_reward_from_id(quest_id)
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
                                await db_manager.add_item_to_inventory(userID, quest_reward, quest_reward_amount)
                                await ctx.send(f"You have completed the quest and been rewarded with {item_name}!, and {quest_xp_reward} xp!")
                            #mark the quest as complete
                            await db_manager.mark_quest_completed(userID, quest_id)
                #get all the info on the drop item
                #TODO: fix this to work with new system
                item_name = await db_manager.get_basic_item_name(monster_drop)
                item_price = await db_manager.get_basic_item_price(monster_drop)
                item_type = await db_manager.get_basic_item_type(monster_drop)
                item_emoji = await db_manager.get_basic_item_emote(monster_drop)
                item_rarity = await db_manager.get_basic_item_rarity(monster_drop)
                #convert the item name to str
                item_name = str(item_name)
                #convert the item price to int
                item_price = int(item_price)
                #convert the item type to str
                item_type = str(item_type)
                #convert the item emoji to str
                item_emoji = str(item_emoji)
                #convert the item rarity to sr
                item_rarity = str(item_rarity)
                
                
                #TODO - Fix this to work with new system
                #calculate the how many items the user will get
                #get the drop chance
                monster_drop_chance = int(monster_drop_chance)
                #get the drop min and max
                monster_drop_min = int(monster_drop_min)
                monster_drop_max = int(monster_drop_max)
                #get a random number between the min and max
                drop_amount = random.randint(monster_drop_min, monster_drop_max)
                #get a random number between 1 and 100
                drop_chance = random.randint(1, 100)
                #if the drop chance is less than or equal to the monsters drop chance
                if drop_chance <= monster_drop_chance:
                    #give the user the drop
                    await db_manager.add_item_to_inventory(userID, monster_drop, drop_amount)
                    #send a message to the channel saying the user got the drop
                    await ctx.send(userName + " has gotten " + str(drop_amount) + " " + monster_drop + "!")
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
                    await ctx.send(userName + " has leveled up! They are now level " + str(new_level) + "!")
                #set the enemys health back to full
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
                monster_health = monster_health - 3
                
            #if the enemy is poisoned, deal 1 damage to them
            isPoisoned = await db_manager.check_enemy_poisoned(monsterID)
            if isPoisoned:
                monster_health = monster_health - 1
                
            #get the monsters attack
            monster_attack = await db_manager.get_enemy_damage(monsterID)
            #convert the attack to int
            monster_attack = int(monster_attack[0])
            #monsters defence is half of their health
            monster_defence = await db_manager.get_enemy_health(monsterID)
            #convert the defence to int
            monster_defence = int(monster_defence[0])
            #divide the defence by 2
            monster_defence = monster_defence / 5
            
            #get the users armor
            user1_armor = await db_manager.get_equipped_armor(userID)
            if user1_armor == None or user1_armor == []:
                user1_armor_name = "Clothes"
                user1_defense = 0
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
            
            userName = str(userName)
            #calculate the damage
            damage = monster_attack - user1_defense
            
            #TODO - Fix this to work with new system
            user1_fire_resistance = await db_manager.get_fire_resistance(userID)
            user1_paralyze_resistance = await db_manager.get_paralysis_resistance(userID)
            user1_poison_resistance = await db_manager.get_poison_resistance(userID)
            
            isSetONFire = random.randint(1, 10)
            #if the fire resistance / 10 is greater than the number, the user is immune to fire
            if user1_fire_resistance / 10 >= isSetONFire:
                isSetONFire = 0
            
            #have the user have a 1/10 chance of being poisoned
            #if the poison resistance / 10 is greater than the number, the user is immune to poison
            isPoisoned = random.randint(1, 10)
            if user1_poison_resistance / 10 >= isPoisoned:
                isPoisoned = 0
                
            #a 1/10 chance of being paralyzed
            isParalyzed = random.randint(1, 10)
            #if the paralysis resistance / 10 is greater than the number, the user is immune to paralysis
            if user1_paralyze_resistance / 10 >= isParalyzed:
                isParalyzed = 0
            #if the sub type is Fire tell the user they were set on fire and add a (burning) to the end of the damage
            monster_element = await db_manager.get_enemy_element(monsterID)
            if monster_element == "Fire" and isSetONFire == 1:
                Newdescription = prev_desc + f" and set {userName} on Fire."
                #set the users burn status to true
                await db_manager.set_user_burning(userID)
                #mark the turn the user was set on fire
                user_burn_turn = turnCount
                
            #if the user is poisoned, tell the user they were poisoned, skip their turn and add a (poisoned) to the end of the damage
            elif monster_element == "Poison" and isPoisoned == 1:
                Newdescription = prev_desc + f"and Poisoned {userName}."
                #set the users poison status to true
                await db_manager.set_user_poisoned(userID)
                #mark the turn the user was poisoned
                user_poison_turn = turnCount

            #if the subtype is paralyze, tell the user they were paralyzed and skip their turn
            elif monster_element == "Paralyze" and isParalyzed == 1:
                Newdescription = prev_desc + "and Paralyzed " + userName + "."
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
            #monster_crit_chance = int(monster_crit_chance[0])
            #get a random number between 1 and 100
            crit_chance = random.randint(1, 100)
            #if the crit chance is less than or equal to the monsters crit chance
            #if the damage is less than 0, set it to 0
            if damage < 0:
                damage = 0
            #if the monsters attack is less than the users defense, set the damage to 0
            if monster_attack < user1_defense:
                damage = 0
            #if the damage is greater than the users health, set the damage to the users health
            #remove the () from the users health
            user_health = str(user_health)
            user_health = user_health.replace("(", "")
            user_health = user_health.replace(")", "")
            #remove the ,
            user_health = user_health.replace(",", "")
            user_health = int(user_health)
            if damage > user_health:
                damage = user_health
            #remove the damage from the users health
            #roll for dodge chance
            dodge_chance = random.randint(1, 100)
            #get the users dodge chance
            user_dodge_chance = await db_manager.get_dodge_chance(userID)
            #if the dodge chance is less than or equal to the users dodge chance, tell the user they dodged the attack
            if dodge_chance <= user_dodge_chance:
                Newdescription = prev_desc + f" {userName} Dodged the attack."
                damage = 0
            await db_manager.remove_health(userID, damage)
            
            #import the json of the enemyPromts
                        
            #TODO: fix promts to work with new system
            #get the enemy promts
            enemyPromts = await db_manager.get_enemy_quotes(monsterID)
            #if the promts are empty, set them to a default message
            if enemyPromts == None or enemyPromts == "" or enemyPromts == [] or enemyPromts == "None" or enemyPromts == monsterID:
                enemyPromt = f"{monsterName} attacked {userName} for {damage} damage."
                enemyPromt = enemyPromt.replace("{damage}", str(damage))
                #replace the {target} with the users name
                enemyPromt = enemyPromt.replace("{target}", userName)
                #replace the {enemy} with the monsters name
                enemyPromt = enemyPromt.replace("{enemy_name}", monsterName)
            else:
                #pick a random enemy promt
                enemyPromt = random.choice(enemyPromts)
                if enemyPromt == monsterID:
                    enemyPromt = f"{monsterName} attacked {userName} for {damage} damage."
                    enemyPromt = str(enemyPromt)
                    #replace the {damage} with the damage
                    enemyPromt = enemyPromt.replace("{damage}", str(damage))
                    #replace the {target} with the users name
                    enemyPromt = enemyPromt.replace("{target}", userName)
                    #replace the {enemy} with the monsters name
                    enemyPromt = enemyPromt.replace("{enemy_name}", monsterName)
                else:
                    enemyPromt = str(enemyPromt)
                    #replace the {damage} with the damage
                    enemyPromt = enemyPromt.replace("{damage}", str(damage))
                    #replace the {target} with the users name
                    enemyPromt = enemyPromt.replace("{target}", userName)
                    #replace the {enemy} with the monsters name
                    enemyPromt = enemyPromt.replace("{enemy_name}", monsterName)
                    #CONVERT THE PROMTS TO A STRING
                    enemyPromt = str(enemyPromt)
            if crit_chance <= monster_crit_chance:
                #double the damage
                damage = damage * 2
                #set newdriscription to the crit message
                enemyPromt = enemyPromt + f" and hit a Crit !"
            Newdescription = prev_desc + "\n" + f"{enemyPromt}"
            #convert the embed to a string
            Newdescription = str(Newdescription)
            #if there are more than 4 lines in the embed, remove the first line
            if Newdescription.count("\n") >= 3:
                Newdescription = Newdescription.split("\n", 1)[1]
            #edit the embed feilds to include the new health
            user1_health = await db_manager.get_health(userID)
            monster_health = monster_health
            #remove the () and , from the health
            user1_health = str(user1_health).replace("(", "")
            user1_health = str(user1_health).replace(")", "")
            user1_health = str(user1_health).replace(",", "")
            monster_health = str(monster_health).replace("(", "")
            monster_health = str(monster_health).replace(")", "")
            monster_health = str(monster_health).replace(",", "")
            #convert to int
            user1_health = int(user1_health)
            monster_health = int(monster_health)
            
            #if the user is dead, set their health to 0
            if user1_health <= 0:
                user1_health = 0
            if monster_health <= 0:
                monster_health = 0

            #convert back to string
            user1_health = str(user1_health)
            monster_health = str(monster_health)
            
            if await db_manager.check_user_burning(userID):
                await db_manager.remove_health(userID, 1)
                #add a (burning) to the users health
                user1_health = user1_health + " (burning)"
                #mark down the turn count when the user was set on fire
                
            if await db_manager.check_enemy_burning(monsterID):
                monster_health = monster_health - 1
                #add a (burning) to the users health
                monster_health = monster_health + " (burning)"
                #mark down the turn count when the user was set on fire

            if await db_manager.check_user_poisoned(userID):
                await db_manager.remove_health(userID, 3)
                #add a (poisoned) to the users health
                user1_health = user1_health + " (poisoned)"
                #mark down the turn count when the user was set on fire
            
            if await db_manager.check_enemy_poisoned(monsterID):
                monster_health = monster_health - 3
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
            embed.add_field(name=userName, value="Health: " + user1_health, inline=True)
            monster_health = str(monster_health)
            embed.add_field(name=monster_name, value="Health: " + monster_health, inline=True)
            monster_health = int(monster_health)
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
                await ctx.send(userName + " has died!")
                #set the users health to 0
                await db_manager.set_health(userID, 0)
                #set the user as dead 
                await db_manager.set_dead(userID)
                #set the user not in combat
                await db_manager.set_not_in_combat(userID)
                return userID
            
            
            
#a function for just a regular attack, basically the turn system, but its one turn only, and it doesnt have the turn count, its just the user attacking the monster then the monster attacking the user and thats it
async def attack(ctx: Context, userID, userName, monsterID, monsterName):
    #calculate the damage the user does
    try:
        user_weapon = await db_manager.get_equipped_weapon(userID)
        print(user_weapon[0])
        print(user_weapon[0][1])
        user_weapon_id = user_weapon[0][1]
        user_weapon_name = user_weapon[0][2]
        user_weapon_emoji = user_weapon[0][4]
        user_weapon_damage = user_weapon[0][8]
        user_weapon_damage = str(user_weapon_damage)
        #split the damage by the -
        user_weapon_damage = user_weapon_damage.split("-")
        #get a random number between the two
        user_weapon_damage = random.randint(int(user_weapon_damage[0]), int(user_weapon_damage[1]))
    except(IndexError, TypeError):
        await ctx.send("You dont have a weapon equipped!")
    
    try: 
        user_armor = await db_manager.get_equipped_armor(userID)
    except(IndexError, TypeError):
        user_armor = 0
        
    try:
        user_defense = user_armor[0][8]
    except(IndexError, TypeError):
        user_defense = 0
    
    user_damage_boost = await db_manager.get_damage_boost(userID)
    user_damage_boost = int(user_damage_boost)
    user_weapon_damage = user_weapon_damage + user_damage_boost
    
    #get the monsters health
    monsterTotalHealth = await db_manager.get_enemy_health(monsterID)
    monsterDamage = await db_manager.get_enemy_damage(monsterID)
    #seperate the attack by the - and get a random number between the two
    monsterDamage = monsterDamage[0]
    monsterDamage = monsterDamage.split("-")
    monsterDamage = random.randint(int(monsterDamage[0]), int(monsterDamage[1]))
    #convert it to int 
    monsterTotalHealth = int(monsterTotalHealth[0])
    
    #calculate the damage the user does
    user_damage = user_weapon_damage
    #send a message to the channel the quoute 
    
    #if the monster or user is not dead
    user_weapon_quotes = await db_manager.get_item_quotes(user_weapon_id)
    #for each quote, remove the itemid 
    quotes = []
    for quote in user_weapon_quotes:
        quote = str(quote)
        quote = quote.replace(f"('{user_weapon_id}',", "")
        quote = quote.replace(")", "")
        quote = quote.replace("'", "")
        quotes.append(quote)
        
    user1Promt = random.choice(quotes)
    monster_defence = await db_manager.get_enemy_health(monsterID)
    #convert the defence to int
    monster_defence = int(monster_defence[0])
    #divide the defence by 5
    monster_defence = monster_defence / 5
    #convert the defence to int
    monster_defence = int(monster_defence)
    #calculate the damage the the user does
    user_damage = user_weapon_damage - monster_defence
    if user1Promt == user_weapon:
        user1Promt = random.choice(user_weapon_quotes)
    user1Promt = str(user1Promt)
    user1Promt = user1Promt.replace("{user}", userName)
    user1Promt = user1Promt.replace("{target}", monsterName)
    user1Promt = user1Promt.replace("{damage}", str(user_damage))
    monster_attack = await db_manager.get_enemy_damage(monsterID)
    #monsters defence is half of their health
    #get the damage dealers
    first_damage_dealer = await db_manager.get_firstDamageDealer(monsterID, ctx.guild.id)
    second_damage_dealer = await db_manager.get_secondDamageDealer(monsterID, ctx.guild.id)
    third_damage_dealer = await db_manager.get_thirdDamageDealer(monsterID, ctx.guild.id)
    
    print(first_damage_dealer)
    print(second_damage_dealer)
    print(third_damage_dealer)
    
    
    #get the damage done
    first_damage = await db_manager.get_firstDamage(monsterID, ctx.guild.id)
    second_damage = await db_manager.get_secondDamage(monsterID, ctx.guild.id)
    third_damage = await db_manager.get_thirdDamage(monsterID, ctx.guild.id)
    print(first_damage)
    print(second_damage)
    print(third_damage)

    #check if the damage dealers are NoneType
    if first_damage_dealer == None:
        first_damage = 0
        
    if second_damage_dealer == None:
        second_damage = 0
    
    if third_damage_dealer == None:
        third_damage = 0
        
    #get the damage dealers
    first_damage_dealer = await db_manager.get_firstDamageDealer(monsterID, ctx.guild.id)     
    second_damage_dealer = await db_manager.get_secondDamageDealer(monsterID, ctx.guild.id)     
    third_damage_dealer = await db_manager.get_thirdDamageDealer(monsterID, ctx.guild.id)
    
    #check if the dealers are none
    if first_damage_dealer is None:
        first_damage_dealer = userID
        await db_manager.edit_firstDamageDealer(monsterID, ctx.guild.id, userID)
        await db_manager.edit_firstDamage(monsterID, ctx.guild.id, user_damage)
        await db_manager.edit_nameOfFirstDamageDealer(monsterID, ctx.guild.id, userName)
    elif user_damage > await db_manager.get_firstDamage(monsterID, ctx.guild.id):
        third_damage_dealer = second_damage_dealer
        second_damage_dealer = first_damage_dealer
        first_damage_dealer = userID
        await db_manager.edit_firstDamageDealer(monsterID, ctx.guild.id, userID)
        await db_manager.edit_firstDamage(monsterID, ctx.guild.id, user_damage)
        await db_manager.edit_nameOfFirstDamageDealer(monsterID, ctx.guild.id, userName)
    elif second_damage_dealer is None:
        second_damage_dealer = userID
        await db_manager.edit_secondDamageDealer(monsterID, ctx.guild.id, userID)
        await db_manager.edit_secondDamage(monsterID, ctx.guild.id, user_damage)
        await db_manager.edit_nameOfSecondDamageDealer(monsterID, ctx.guild.id, userName)
    elif user_damage > await db_manager.get_secondDamage(monsterID, ctx.guild.id):
        third_damage_dealer = second_damage_dealer
        second_damage_dealer = userID
        await db_manager.edit_secondDamageDealer(monsterID, ctx.guild.id, userID)
        await db_manager.edit_secondDamage(monsterID, ctx.guild.id, user_damage)
        await db_manager.edit_nameOfSecondDamageDealer(monsterID, ctx.guild.id, userName)
    elif third_damage_dealer is None:
        third_damage_dealer = userID
        await db_manager.edit_thirdDamageDealer(monsterID, ctx.guild.id, userID)
        await db_manager.edit_thirdDamage(monsterID, ctx.guild.id, user_damage)
        await db_manager.edit_nameOfThirdDamageDealer(monsterID, ctx.guild.id, userName)
    elif user_damage > await db_manager.get_thirdDamage(monsterID, ctx.guild.id):
        third_damage_dealer = userID
        await db_manager.edit_thirdDamageDealer(monsterID, ctx.guild.id, userID)
        await db_manager.edit_thirdDamage(monsterID, ctx.guild.id, user_damage)
        await db_manager.edit_nameOfThirdDamageDealer(monsterID, ctx.guild.id, userName)
        
    #get the damage dealers and damage
    first_damage_dealer = await db_manager.get_firstDamageDealer(monsterID, ctx.guild.id)
    second_damage_dealer = await db_manager.get_secondDamageDealer(monsterID, ctx.guild.id)
    third_damage_dealer = await db_manager.get_thirdDamageDealer(monsterID, ctx.guild.id)
    first_damage = await db_manager.get_firstDamage(monsterID, ctx.guild.id)
    second_damage = await db_manager.get_secondDamage(monsterID, ctx.guild.id)
    third_damage = await db_manager.get_thirdDamage(monsterID, ctx.guild.id)
        
    print(f"{first_damage_dealer} {str(first_damage)}")
    print(f"{second_damage_dealer} {str(second_damage)}")
    print(f"{third_damage_dealer} {str(third_damage)}")
             
    #deal the damage to the monster
    await db_manager.remove_spawned_monster_health(monsterID, ctx.guild.id, user_damage)
    currentHealth = await db_manager.get_spawned_monster_health(monsterID, ctx.guild.id)
    print(currentHealth)
    if currentHealth <= 0:
        currentHealth = 0
    #convert the health to int
    #send a message to the channel the quoute
    await ctx.send(user1Promt + f" {monsterName} has {currentHealth}/{monsterTotalHealth} health left!")
    #wait 3 seconds
    await asyncio.sleep(3)
    
    enemyPromts = await db_manager.get_enemy_quotes(monsterID)
    #if the promts are empty, set them to a default message
    if enemyPromts == None or enemyPromts == "" or enemyPromts == [] or enemyPromts == "None" or enemyPromts == monsterID:
        enemyPromt = f"{monsterName} attacked {userName} for {monsterDamage} damage."
        enemyPromt = enemyPromt.replace("{damage}", str(monsterDamage))
        #replace the {target} with the users name
        enemyPromt = enemyPromt.replace("{target}", userName)
        #replace the {enemy} with the monsters name
        enemyPromt = enemyPromt.replace("{enemy_name}", monsterName)
    else:
        #pick a random enemy promt
        enemyPromt = random.choice(enemyPromts)
        if enemyPromt == monsterID:
            enemyPromt = f"{monsterName} attacked {userName} for {monsterDamage} damage."
            enemyPromt = str(enemyPromt)
            #replace the {damage} with the damage
            enemyPromt = enemyPromt.replace("{damage}", str(monsterDamage))
            #replace the {target} with the users name
            enemyPromt = enemyPromt.replace("{target}", userName)
            #replace the {enemy} with the monsters name
            enemyPromt = enemyPromt.replace("{enemy_name}", monsterName)
        else:
            enemyPromt = str(enemyPromt)
            #replace the {damage} with the damage
            enemyPromt = enemyPromt.replace("{damage}", str(monsterDamage))
            #replace the {target} with the users name
            enemyPromt = enemyPromt.replace("{target}", userName)
            #replace the {enemy} with the monsters name
            enemyPromt = enemyPromt.replace("{enemy_name}", monsterName)
            #CONVERT THE PROMTS TO A STRING
            enemyPromt = str(enemyPromt)
    #send the message to the channel
    
    
    #deal the damage to the user
    monsterDamage = monsterDamage - user_defense
    #get the users dodge chance
    user_dodge_chance = await db_manager.get_dodge_chance(userID)
    luck = await db_manager.get_luck(userID)
    #convert the dodge chance to int
    user_dodge_chance = int(user_dodge_chance)
    user_dodge_chance = user_dodge_chance + luck
    #get a random number between 1 and 100
    random_number = random.randint(1, 100)
    #if the random number is less than or equal to the dodge chance
    if random_number <= user_dodge_chance:
        #send a message saying the user dodged the attack
        await ctx.send(f"{userName} dodged {monsterName}'s attack!")
        #return
        return
    await db_manager.remove_health(userID, monsterDamage)
    await ctx.send(enemyPromt)
    
    #get the users health
    userHealth = await db_manager.get_health(userID)
    #convert it to int 
    userHealth = int(userHealth[0])
    #if the users health is less than or equal to 0, end the fight
    if userHealth <= 0:
        await db_manager.remove_current_spawn(ctx.guild.id)
        #get the monsters name
        #convert the name to str
        monster_name = await db_manager.get_enemy_name(monsterID)
        monster_name = str(monster_name)
        #send a message to the channel saying the user has died
        await ctx.send("**"+ userName + "** has died!")
        #set the users health to 0
        await db_manager.set_health(userID, 0)
        #set the user as dead 
        await db_manager.set_dead(userID)
        #set the user not in combat
        await db_manager.set_not_in_combat(userID)
        return userID
    #get the monsters health
    monsterHealth = await db_manager.get_spawned_monster_health(monsterID, ctx.guild.id)
    if monsterHealth < 0:
        monsterHealth = 0
    print("monster health: " + str(monsterHealth))
    #convert it to int
    #if the monsters health is less than or equal to 0, end the fight
    if monsterHealth <= 0:
        #remove the monster from the spawn
        await ctx.send(f"{monsterName} has died!")
        monster_drops = await db_manager.get_enemy_drops(monsterID) 
        luck = await db_manager.get_luck(userID)
        drops = []
        for drop in monster_drops:
            item = drop[1]
            drop_amount = drop[2]
            drop_chance = drop[3]
            drop_chance = float(drop_chance)
            drop_amount = int(drop_amount)
            drops.append([item, drop_chance, drop_amount])

        #organize the hunt items by their hunt chance
        drops.sort(key=lambda x: x[1], reverse=True)
        print(drops)
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
        for item in drops:
            if item[1] <= 0.1:
                lowchanceitems.append(item)

        midchanceitems = []
        for item in drops:
            if item[1] > 0.1 and item[1] <= 0.5:
                midchanceitems.append(item)

        highchanceitems = []
        for item in drops:
            if item[1] > 0.5 and item[1] <= 1:
                highchanceitems.append(item)

        #based on the roll, get the item
        if roll <= 10:
            try:
                item = random.choice(lowchanceitems)
            except(IndexError):
                item = random.choice(drops)
        elif roll > 10 and roll <= 50:
            try:
                item = random.choice(midchanceitems)
            except(IndexError):
                item = random.choice(lowchanceitems)
        elif roll > 50 and roll <= 100:
            try:
                item = random.choice(highchanceitems)
            except(IndexError):
                item = random.choice(midchanceitems)
        
        
        #get the damage dealers
        first_damage_dealer = await db_manager.get_firstDamageDealer(monsterID, ctx.guild.id)     
        second_damage_dealer = await db_manager.get_secondDamageDealer(monsterID, ctx.guild.id)     
        third_damage_dealer = await db_manager.get_thirdDamageDealer(monsterID, ctx.guild.id)
        
        print(first_damage_dealer)
        print(second_damage_dealer)
        print(third_damage_dealer)

        #set None values to default
        if first_damage_dealer is None:
            first_damage_dealer = -1
        if second_damage_dealer is None:
            second_damage_dealer = -1
        if third_damage_dealer is None:
            third_damage_dealer = -1

        #get the damage dealers names
        #get the users name
        
        first_dealer_name = await db_manager.get_nameOfFirstDamageDealer(monsterID, ctx.guild.id)
        second_dealer_name = await db_manager.get_nameOfSecondDamageDealer(monsterID, ctx.guild.id)
        third_dealer_name = await db_manager.get_nameOfThirdDamageDealer(monsterID, ctx.guild.id)

        
        #get the damage dealers damage
        first_dealer_damage = await db_manager.get_firstDamage(monsterID, ctx.guild.id)
        second_dealer_damage = await db_manager.get_secondDamage(monsterID, ctx.guild.id)
        third_dealer_damage = await db_manager.get_thirdDamage(monsterID, ctx.guild.id)
        
        #assign the items based on damage dealt and chance
        first_dealer_items = []
        if first_dealer_damage >= second_dealer_damage and first_dealer_damage >= third_dealer_damage:
            first_dealer_items = highchanceitems + midchanceitems + lowchanceitems
        elif first_dealer_damage < second_dealer_damage and second_dealer_damage >= third_dealer_damage:
            first_dealer_items = midchanceitems + highchanceitems + lowchanceitems
        else:
            first_dealer_items = midchanceitems + lowchanceitems + highchanceitems
        
        second_dealer_items = []
        if second_dealer_damage >= first_dealer_damage and second_dealer_damage >= third_dealer_damage:
            second_dealer_items = midchanceitems + lowchanceitems
        else:
            second_dealer_items = lowchanceitems
        
        third_dealer_items = midchanceitems + lowchanceitems
        
        #iterate through each damage dealer and assign them their items
        for dealer_id, dealer_name, dealer_damage, dealer_items in zip([first_damage_dealer, second_damage_dealer, third_damage_dealer], [first_dealer_name, second_dealer_name, third_dealer_name], [first_dealer_damage, second_dealer_damage, third_dealer_damage], [first_dealer_items, second_dealer_items, third_dealer_items]):
            #if the dealer is none, skip
            if dealer_id is None:
                continue
            #if the dealer has no name, skip
            if dealer_name is None:
                continue
            #if the dealer has no damage, skip
            if dealer_damage is None:
                continue
            emote = None
            item_name = None
            item_amount = None
            for item in dealer_items:
                roll = random.randint(1, 100) - luck
                if roll > item[1]:
                    continue
                emote = await db_manager.get_basic_item_emote(item[0])
                item_name = await db_manager.get_basic_item_name(item[0])
                item_amount = item[2]
                await db_manager.add_item_to_inventory(dealer_id, item[0], item[2])
                break
            if emote and item_name and item_amount:
                await ctx.send(dealer_name + " has gotten " + str(item_amount) + " " + emote +  "**" + item_name + "**!")

            
            #grant the items based on the damage dealers
            
            
                
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
                await ctx.send(userName + " has leveled up! They are now level **" + str(new_level) + "**!")
                #get the users quest
            #check if the user has a quest
            has_quest = await db_manager.check_user_has_any_quest(userID)
            #if the user has a quest
            if has_quest:
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
                            #get the quest reward from the quest id
                            quest_reward = await db_manager.get_quest_reward_from_id(quest_id)
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
                                #add the item to the users inventory
                                await db_manager.add_item_to_inventory(userID, quest_reward, quest_reward_amount)
                                await ctx.send(f"You have completed the quest and been rewarded with {quest_reward_amount} {quest_reward}, and {quest_xp_reward} xp!")
        await db_manager.remove_current_spawn(ctx.guild.id)
        return userID
    
    
    
    
#create a function to spawn a monster
async def spawn_monster(ctx, monsterID):
    #add the monster to the spawns
    #get all the info on the monster, and make it an embed
    monster_name = await db_manager.get_enemy_name(monsterID)
    monster_description = await db_manager.get_enemy_description(monsterID)
    monster_hp = await db_manager.get_enemy_health(monsterID)
    monster_hp = int(monster_hp[0])
    monster_attack = await db_manager.get_enemy_damage(monsterID)
    monster_attack = str(monster_attack)
    #remove the ()
    monster_attack = monster_attack.replace("(", "")
    monster_attack = monster_attack.replace(")", "")
    #remove the ,
    monster_attack = monster_attack.replace(",", "")
    monster_attack = monster_attack.replace("'", "")
    #space out the attack
    monster_attack = monster_attack.replace("-", " - ")
    
    
    #seperate the attack by the - and get a random number between the two
    monster_emoji = await db_manager.get_enemy_emoji(monsterID)
    monster_emoji = str(monster_emoji[0])
    await db_manager.add_current_spawn(ctx.guild.id, monsterID, monster_hp)
    #send the embed to the channel
    embed = discord.Embed(
        title=f"{monster_name}",
        description=f"**Health:** {monster_hp}/{monster_hp}\n**Attack:** {monster_attack}",
        color=discord.Color.red()
    )
    # If there's an emote for the mob
    if monster_emoji:
        # Get the numbers in the emote string
        emoji_numbers = re.findall(r'\d+', monster_emoji)
        # If there are numbers in the emote string
        if emoji_numbers:
            # If there's an "a" after the first "<", then it's a GIF
            if monster_emoji[1] == "a":
                # Set the emote to the first number in the list
                emoji = emoji_numbers[0]
                # Set the thumbnail to the emote
                embed.set_thumbnail(url=f"https://cdn.discordapp.com/emojis/{emoji}.gif")
            # If there's a ":" after the first "<", then it's a PNG
            elif monster_emoji[1] == ":":
                # Set the emote to the first number in the list
                emoji = emoji_numbers[0]
                # Set the thumbnail to the emote
                embed.set_thumbnail(url=f"https://cdn.discordapp.com/emojis/{emoji}.png")
    # Add the footer "use /attack {monster name} to attack the monster"
    embed.set_footer(text=f"use /attack {monsterID} to attack this monster")
    field_text = "No damage has been dealt yet."
    embed.add_field(name="💥 Top Damage Dealers", value=field_text, inline=False)
    # Send the embed to the channel
    await ctx.send(embed=embed)
    
    
async def send_spawned_embed(ctx: Context):
    # Get the current mob spawned
    currentSpawn = await db_manager.get_current_spawn(ctx.guild.id)
    currentSpawn = currentSpawn[0]

    # If there is no mob spawned
    if not currentSpawn:
        # Send a message saying there is no mob spawned
        await ctx.send("There is no mob spawned!")
    else:
        # Get the mob name, health, and emote
        mobName = await db_manager.get_enemy_name(currentSpawn)
        mobHealth = await db_manager.get_enemy_health(currentSpawn)
        mobHealth = int(mobHealth[0])
        mobAttack = await db_manager.get_enemy_damage(currentSpawn)
        currentHealth = await db_manager.get_spawned_monster_health(currentSpawn, ctx.guild.id)
        mobEmoji = await db_manager.get_enemy_emoji(currentSpawn)
        mobEmoji = str(mobEmoji[0])

        # Convert everything to str
        mobName = str(mobName)
        mobHealth = str(mobHealth)
        mobAttack = str(mobAttack)
        #remove the ' ' from the attack
        mobAttack = mobAttack.replace("'", "")
        #space out the attack
        mobAttack = mobAttack.replace("-", " - ")
        mobEmoji = str(mobEmoji)

        # Remove the () and , from the strings
        mobName = mobName.replace("(", "")
        mobName = mobName.replace(")", "")
        mobName = mobName.replace(",", "")
        mobHealth = mobHealth.replace("(", "")
        mobHealth = mobHealth.replace(")", "")
        mobHealth = mobHealth.replace(",", "")
        mobAttack = mobAttack.replace("(", "")
        mobAttack = mobAttack.replace(")", "")
        mobAttack = mobAttack.replace(",", "")
        mobEmoji = mobEmoji.replace("(", "")
        mobEmoji = mobEmoji.replace(")", "")
        mobEmoji = mobEmoji.replace(",", "")

        # Build the embed, and set the image to the monster's emoji
        embed = discord.Embed(
            title=f"{mobName}",
            description=f"**Health:** {currentHealth}/{mobHealth}\n**Attack:** {mobAttack}",
            color=discord.Color.red()
        )

        # If there's an emote for the mob
        if mobEmoji:
            # Get the numbers in the emote string
            emoji_numbers = re.findall(r'\d+', mobEmoji)
            # If there are numbers in the emote string
            if emoji_numbers:
                # If there's an "a" after the first "<", then it's a GIF
                if mobEmoji[1] == "a":
                    # Set the emote to the first number in the list
                    emoji = emoji_numbers[0]
                    # Set the thumbnail to the emote
                    embed.set_thumbnail(url=f"https://cdn.discordapp.com/emojis/{emoji}.gif")
                # If there's a ":" after the first "<", then it's a PNG
                elif mobEmoji[1] == ":":
                    # Set the emote to the first number in the list
                    emoji = emoji_numbers[0]
                    # Set the thumbnail to the emote
                    embed.set_thumbnail(url=f"https://cdn.discordapp.com/emojis/{emoji}.png")

        # Add the footer "use /attack {monster name} to attack the monster"
        embed.set_footer(text=f"use /attack {currentSpawn} to attack this monster")
        # Get the top 3 damage dealers
        first_damage_dealer = await db_manager.get_firstDamageDealer(currentSpawn, ctx.guild.id)
        second_damage_dealer = await db_manager.get_secondDamageDealer(currentSpawn, ctx.guild.id)
        third_damage_dealer = await db_manager.get_thirdDamageDealer(currentSpawn, ctx.guild.id)
        print(first_damage_dealer)

        # Add a field for the top 3 damage dealers
        field_text = ""
        if first_damage_dealer != 0 and first_damage_dealer != None and first_damage_dealer != "None":
            field_text += f"🏆 1st Place: <@{first_damage_dealer}> - They get loot!\n"
        if second_damage_dealer != 0 and second_damage_dealer != None and second_damage_dealer != "None":
            field_text += f"🥈 2nd Place: <@{second_damage_dealer}> - They get loot!\n"
        if third_damage_dealer != 0 and third_damage_dealer != None and third_damage_dealer != "None":
            field_text += f"🥉 3rd Place: <@{third_damage_dealer}> - They get loot!\n"
        if not field_text:
            field_text = "No damage has been dealt yet."
        embed.add_field(name="💥 Top Damage Dealers", value=field_text, inline=False)
        # Send the embed to the channel
        await ctx.send(embed=embed)
    
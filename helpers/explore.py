import asyncio
import datetime
import json
import random
import re
import requests
from discord import Webhook, SyncWebhook
import aiohttp
import discord
from discord import Embed, app_commands
from discord.ext import commands
from discord.ext.commands import Context, has_permissions

from helpers import battle, checks, db_manager, hunt, mine

cash = "<:cash:1077573941515792384>"
@commands.cooldown(1, 300, commands.BucketType.user)
async def explore(self, ctx: Context, structure: str):
    #check if the user exists in the database
    if await db_manager.check_user(ctx.author.id) == 0:
        await ctx.send("You don't have an account! Use `/start` to start your adventure!")
        await self.explore.reset_cooldown(ctx)
        return
    #get the current structure in the channel
    await db_manager.add_explorer_log(ctx.guild.id, ctx.author.id)
    structure_outcomes = await db_manager.get_structure_outcomes(structure)
    msg = ctx.message
    #get the structure outcomes
    luck = await db_manager.get_luck(msg.author.id)
    #for each outcome, calculate the chance of it happening based on the outcome chance and the users luck
        #get the hunt chance for each item in the huntitems list
    outcomes = []
    for outcome in structure_outcomes:
        #print(outcome)
        #print(len(outcome))
        #`structure_quote` varchar(255) NOT NULL,
        #`structure_state` varchar(255) NOT NULL,
        #`outcome_chance` int(11) NOT NULL,
        #`outcome_type` varchar(255) NOT NULL,
        #`outcome` varchar(255) NOT NULL,
        #`outcome_amount` varchar(11) NOT NULL,
        #`outcome_money` varchar(11) NOT NULL,
        #`outcome_xp` varchar(11) NOT NULL,
        quote = outcome[1]
        state = outcome[2]
        outcome_chance = outcome[3]
        outcome_type = outcome[4]
        outcome_thing = outcome[5]
        outcome_amount = outcome[6]
        outcome_money = outcome[7]
        outcome_xp = outcome[8]
        #add the outcome to the outcomes list
        outcomes.append([quote, state, outcome_chance, outcome_type, outcome_thing, outcome_amount, outcome_money, outcome_xp])
    
    #sort the outcomes list by the chance of the outcome happening
    outcomes.sort(key=lambda x: x[2], reverse=True)
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
    for item in outcomes:
        if item[2] <= 0.1:
            lowchanceitems.append(item)
    midchanceitems = []
    for item in outcomes:
        if item[2] > 0.1 and item[2] <= 0.5:
            midchanceitems.append(item)
    highchanceitems = []
    for item in outcomes:
        if item[2] > 0.5 and item[2] <= 1:
            highchanceitems.append(item)
    #based on the roll, get the item
    if roll <= 10:
        try:
            item = random.choice(lowchanceitems)
        except(IndexError):
            item = random.choice(outcomes)
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
    
    #get the info of the item
    outcome_quote = item[0]
    outcome_state = item[1]
    outcome_chance = item[2]
    outcome_type = item[3]
    outcome_thing = item[4]
    outcome_amount = item[5]
    outcome_money = item[6]
    outcome_xp = item[7]
    
    #the outcome_types are: item_gain, item_loss, health_loss, health_gain, money_gain, money_loss, spawn
    #if the outcome type is item_gain
    #get the outcome_icon
    #remove the line breaks from the outcome_quote
    outcome_thing = str(outcome_thing)
    outcome_quote = str(outcome_quote)
    outcome_quote = outcome_quote.strip()
    if outcome_type == "item_gain":
        #if outcome things first word is chest, then add a to the end of the outcome_quote
        if outcome_thing.split("_")[0] == "chest":
            outcome_icon = await db_manager.get_chest_icon(outcome_thing)
            outcome_name = await db_manager.get_chest_name(outcome_thing)
        else:
            outcome_name = await db_manager.get_basic_item_name(outcome_thing)
            outcome_icon = await db_manager.get_basic_item_emote(outcome_thing)
        #send a message saying the outcome, and the item gained
        await ctx.send(f"{outcome_quote} + {outcome_amount} {outcome_icon} **{outcome_name}** ...And + ⭐{outcome_xp} XP!")
        #remove the health from the users health
        await db_manager.add_xp(msg.author.id, outcome_xp)
        #check if the user leveled up
        canLevelUp = await db_manager.can_level_up(msg.author.id)
        if canLevelUp == True:
            level = await db_manager.get_level(msg.author.id)
            #remove the () and , from the level
            level = str(level)
            level = level.replace("(", "")
            level = level.replace(")", "")
            level = level.replace(",", "")
            #if the user leveled up, send a message saying they leveled up
            await ctx.send(f"Congrats {msg.author.mention}, you leveled up! You are now level {level}!")
            
        userquest = await db_manager.get_user_quest(msg.author.id)
        if userquest != 0:
            #check if the users quest objective is to get an item and if the item is the item they got
            quest_objective = await db_manager.get_quest_objective_from_id(userquest)
            #seperate it by space and get the second thing
            quest_objective = quest_objective.split(" ")
            quest_objective = quest_objective[1]
            if quest_objective == outcome_thing:
                #add one to the users quest progress
                await db_manager.update_quest_progress(msg.author.id, userquest, outcome_amount)
                #check the users quest progress
                progress = await db_manager.get_quest_progress(msg.author.id, userquest)
                total = await db_manager.get_quest_total_from_id(userquest)
                #if the progress is less than the total, complete the quest and give the user the reward
                if progress >= total:
                    #get quest reward type
                    quest_reward_type = await db_manager.get_quest_reward_type_from_id(userquest)
                    #if the quest reward type is item, give the user the item, and if its Money, give the user the money
                    if quest_reward_type == "item":
                        #get quest reward
                        quest_reward = await db_manager.get_quest_reward_from_id(userquest)
                        #get quest reward amount
                        quest_reward_amount = await db_manager.get_quest_reward_amount_from_id(userquest)
                        #add the item to the users inventory
                        await db_manager.add_item_to_inventory(msg.author.id, quest_reward, quest_reward_amount)
                        await ctx.send(f"Congrats {msg.author.mention}, you completed the quest **{await db_manager.get_quest_name_from_quest_id(userquest)}** and got x{quest_reward_amount} {await db_manager.get_basic_item_emote(quest_reward)} **{await db_manager.get_basic_item_name(quest_reward)}**!")
                    elif quest_reward_type == "Money":
                        #get quest reward amount
                        quest_reward_amount = await db_manager.get_quest_reward_amount_from_id(userquest)
                        #add the money to the users money
                        await db_manager.add_money(msg.author.id, quest_reward_amount)
                        await ctx.send(f"Congrats {msg.author.mention}, you completed the quest **{await db_manager.get_quest_name_from_quest_id(userquest)}** and got {cash}{quest_reward_amount} Money!")
                await db_manager.mark_quest_completed(msg.author.id, userquest)
                
        #add the item to the users inventory
        await db_manager.add_item_to_inventory(msg.author.id, outcome_thing, outcome_amount)
    #if the outcome type is item_loss
    elif outcome_type == "item_loss":
        if outcome_thing.split("_")[0] == "chest":
            outcome_icon = await db_manager.get_chest_icon(outcome_thing)
            outcome_name = await db_manager.get_chest_name(outcome_thing)
        else:
            outcome_name = await db_manager.get_basic_item_name(outcome_thing)
            outcome_icon = await db_manager.get_basic_item_emote(outcome_thing)
        #send a message saying the outcome, and the item lost
        await ctx.send(f"{outcome_quote} + {outcome_amount} {outcome_icon} **{outcome_name}** ...And + ⭐{outcome_xp} XP")
        #remove the health from the users health
        await db_manager.add_xp(msg.author.id, outcome_xp)
        #check if the user leveled up
        canLevelUp = await db_manager.can_level_up(msg.author.id)
        if canLevelUp == True:
            #if the user leveled up, send a message saying they leveled up
            level = await db_manager.get_level(msg.author.id)
            #remove the () and , from the level
            level = str(level)
            level = level.replace("(", "")
            level = level.replace(")", "")
            level = level.replace(",", "")
            #if the user leveled up, send a message saying they leveled up
            await ctx.send(f"Congrats {msg.author.mention}, you leveled up! You are now level {level}!")
        #remove the item from the users inventory
        await db_manager.remove_item_from_inventory(msg.author.id, outcome_thing, outcome_amount)
    #if the outcome type is health_loss
    elif outcome_type == "health_loss":
        #send a message saying the outcome, and the health lost
        await ctx.send(f"{outcome_quote} - {outcome_amount} health! ...And + ⭐{outcome_xp} XP")
        #remove the health from the users health
        await db_manager.add_xp(msg.author.id, outcome_xp)
        #check if the user leveled up
        canLevelUp = await db_manager.can_level_up(msg.author.id)
        if canLevelUp == True:
            #if the user leveled up, send a message saying they leveled up
            level = await db_manager.get_level(msg.author.id)
            #remove the () and , from the level
            level = str(level)
            level = level.replace("(", "")
            level = level.replace(")", "")
            level = level.replace(",", "")
            #if the user leveled up, send a message saying they leveled up
            await ctx.send(f"Congrats {msg.author.mention}, you leveled up! You are now level {level}!")
        await db_manager.remove_health(msg.author.id, outcome_amount)
    #if the outcome type is health_gain
    elif outcome_type == "health_gain":
        #send a message saying the outcome, and the health gained
        await ctx.send(f"{outcome_quote} + {outcome_amount} health! ...And + ⭐{outcome_xp} XP")
        #remove the health from the users health
        await db_manager.add_xp(msg.author.id, outcome_xp)
        #check if the user leveled up
        canLevelUp = await db_manager.can_level_up(msg.author.id)
        if canLevelUp == True:
            #if the user leveled up, send a message saying they leveled up
            level = await db_manager.get_level(msg.author.id)
            #remove the () and , from the level
            level = str(level)
            level = level.replace("(", "")
            level = level.replace(")", "")
            level = level.replace(",", "")
            #if the user leveled up, send a message saying they leveled up
            await ctx.send(f"Congrats {msg.author.mention}, you leveled up! You are now level {level}!")
        #add the health to the users health
        await db_manager.add_health(msg.author.id, outcome_amount)
    #if the outcome type is money_gain
    elif outcome_type == "money_gain":
        #send a message saying the outcome, and the money gained
        await ctx.send(f"{outcome_quote} + {cash}{outcome_amount} ...And + ⭐{outcome_xp} XP")
                    #remove the health from the users health
        await db_manager.add_xp(msg.author.id, outcome_xp)
        #check if the user leveled up
        canLevelUp = await db_manager.can_level_up(msg.author.id)
        if canLevelUp == True:
            #if the user leveled up, send a message saying they leveled up
            level = await db_manager.get_level(msg.author.id)
            #remove the () and , from the level
            level = str(level)
            level = level.replace("(", "")
            level = level.replace(")", "")
            level = level.replace(",", "")
            #if the user leveled up, send a message saying they leveled up
            await ctx.send(f"Congrats {msg.author.mention}, you leveled up! You are now level {level}!")
        #add the money to the users money
        await db_manager.add_money(msg.author.id, outcome_amount)
    #if the outcome type is money_loss
    elif outcome_type == "money_loss":
        #send a message saying the outcome, and the money lost
        await ctx.send(f"{outcome_quote} - {cash}{outcome_amount} ...And + ⭐{outcome_xp} XP")
                    #remove the health from the users health
        await db_manager.add_xp(msg.author.id, outcome_xp)
        #check if the user leveled up
        canLevelUp = await db_manager.can_level_up(msg.author.id)
        if canLevelUp == True:
            #if the user leveled up, send a message saying they leveled up
            level = await db_manager.get_level(msg.author.id)
            #remove the () and , from the level
            level = str(level)
            level = level.replace("(", "")
            level = level.replace(")", "")
            level = level.replace(",", "")
            #if the user leveled up, send a message saying they leveled up
            await ctx.send(f"Congrats {msg.author.mention}, you leveled up! You are now level {level}!")
        #remove the money from the users money
        await db_manager.remove_money(msg.author.id, outcome_amount)
    #if the outcome type is battle
    elif outcome_type == "spawn":
        #send a message saying the outcome
        await ctx.send(f"{outcome_quote}")
        #start a battle
        outcome_name = await db_manager.get_enemy_name(outcome_thing)
        await battle.spawn_monster(ctx, outcome_thing)
import asyncio
import datetime
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
from discord import Color, Embed

from helpers import db_manager, battle
import asyncio
import os
import random
from typing import List, Tuple, Union

import discord
from discord.ext import commands
from helpers.card import Card
from PIL import Image
import discordgame as dg

cash = "<:cash:1077573941515792384>"

#slots 2, this time use a new method of creating the slot machine
async def slots(ctx: Context, user, gamble):
    #instead of an embed, use a regular message
    #create the slot machine
    #get the user's money
    money = await db_manager.get_money(user.id)
    #get the users luck
    #get the users equiped item
    luck = await db_manager.get_luck(user.id)
    print(luck)
    #take the money from the user
    await db_manager.remove_money(user.id, gamble)
    await db_manager.add_money_spent(user.id, gamble)
    #make both the money and gamble an int
    money = int(money[0])
    gamble = int(gamble)
    #if the user doesn't have enough money, return
    if money < gamble:
        return await ctx.send(f"**{user.name}** doesn't have enough money to gamble **{gamble}**.")
    slot_machine = await ctx.send(f"**{user.name}** is gambling {cash}**{gamble}**.")
    
    #create a list of all the possible slot machine emojis
    emoji = [
        ":apple:",
        ":cherries:",
        ":grapes:",
        ":lemon:",
        ":peach:",
        ":tangerine:",
        ":watermelon:",
        ":strawberry:",
        ":banana:",
        ":pineapple:",
        ":kiwi:",
        ":pear:",
        ":crown:",
        ":gem:",
    ]
    #edit the message to show the emojis spinning
    #for every emoji in the list, edit the message to show the emoji in the slot
    #SLOT 1
    #get a random emoji from the list, gems are less likely to show up having a 5% chance, and crowns are less likely to show up having a 10% chance, and the user's luck is added to the chance of geting three in a row
    random_number = random.randint(1, 100)
    if random_number <= 5:
        slot1 = ":gem:"
    else:
        slot1 = random.choice(emoji)
        if slot1 == ":gem:":
            slot1 = random.choice(emoji)
    
    if random_number <= 10:
        slot1 = ":crown:"
    else:
        slot1 = random.choice(emoji)
        if slot1 == ":crown:":
            slot1 = random.choice(emoji)

    if random_number <= luck:
        #set the slot to the same emoji as the last slot
        slot1 = slot1
        
    #spin the slot till it gets to the emoji that was chosen
    for i in emoji:
        if i == slot1:
            break
        await slot_machine.edit(content=f"**{user.name}** is gambling {cash}**{gamble}** \n {i} : :question: : :question:")

    #edit the message to show the emoji in the slot
    await slot_machine.edit(content=f"**{user.name}** is gambling {cash}**{gamble}** \n {slot1} : :question: : :question:")
    #for every emoji in the list, edit the message to show the emoji in the slot

    #SLOT 2
    random_number = random.randint(1, 100)
    if random_number <= 5:
        slot2 = ":gem:"
    else:
        slot2 = random.choice(emoji)
        if slot2 == ":gem:":
            slot2 = random.choice(emoji)

    #do the same for crowns, but a 10% chance
    random_number = random.randint(1, 100)
    if random_number <= 10:
        slot2 = ":crown:"
    else:
        slot2 = random.choice(emoji)
        if slot2 == ":crown:":
            slot2 = random.choice(emoji)
            
    if random_number <= luck:
        #set the slot to the same emoji as the last slot
        slot2 = slot1

    #spin the slot till it gets to the emoji that was chosen
    for i in emoji:
        if i == slot2:
            break
        await slot_machine.edit(content=f"**{user.name}** is gambling {cash}**{gamble}** \n {slot1} : {i} : :question:")
    #edit the message to show the emoji in the slot
    await slot_machine.edit(content=f"**{user.name}** is gambling {cash}**{gamble}** \n {slot1} : {slot2} : :question:")
    #for every emoji in the list, edit the message to show the emoji in the slot

    #SLOT 3
    #get a random emoji from the list, gems are less likely to show up having a 5% chance
    random_number = random.randint(1, 100)
    if random_number <= 5:
        slot3 = ":gem:"
    else:
        #pick a random emoji that isn't a gem
        slot3 = random.choice(emoji)
        if slot3 == ":gem:":
            slot3 = random.choice(emoji)

    #do the same for crowns, but a 10% chance
    random_number = random.randint(1, 100)
    if random_number <= 10:
        slot3 = ":crown:"
    else:
        slot3 = random.choice(emoji)
        if slot3 == ":crown:":
            slot3 = random.choice(emoji)
            
    if random_number <= luck:
        #set the slot to the same emoji as the last slot
        slot3 = slot2
    #spin the slot till it gets to the emoji that was chosen
    for i in emoji:
        if i == slot3:
            break
        await slot_machine.edit(content=f"**{user.name}** is gambling {cash}**{gamble}** \n {slot1} : {slot2} : {i}")
    #edit the message to show the emoji in the slot
    await slot_machine.edit(content=f"**{user.name}** is gambling {cash}**{gamble}** \n {slot1} : {slot2} : {slot3}")

    #get the result of each slot
    slot1_result = slot1
    slot2_result = slot2
    slot3_result = slot3

    #check if the slots are the same
    #if any slot is a gem, add the amount they bet  times 1.1 to their balance
    if slot1_result == slot2_result or slot1_result == slot3_result or slot2_result == slot3_result:
        #if 2 of the slots are the same, add the amount they bet  times 1.5 to their balance
        await slot_machine.edit(content=f"**{user.name}** won {cash}**{gamble*3}**! \n {slot1} : {slot2} : {slot3}")
        await db_manager.add_money(user.id, gamble*3)
        await db_manager.add_money_earned(user.id, gamble*3)
    
    elif slot1_result == ":gem:" or slot2_result == ":gem:" or slot3_result == ":gem:":
        await slot_machine.edit(content=f"**{user.name}** won {cash}**{gamble*1.5}**! \n {slot1} : {slot2} : {slot3}")
        await db_manager.add_money(user.id, gamble*1.5)
        await db_manager.add_money_earned(user.id, gamble*1.5)
        
    #if any slot is a crown, add the amount they bet  times 1.2 to their balance
    elif slot1_result == ":crown:" or slot2_result == ":crown:" or slot3_result == ":crown:":
        await slot_machine.edit(content=f"**{user.name}** won {cash}**{gamble*1.2}**! \n {slot1} : {slot2} : {slot3}")
        await db_manager.add_money(user.id, gamble*1.2)
        await db_manager.add_money_earned(user.id, gamble*1.2)

    elif slot1_result == slot2_result == slot3_result == ":gem:":
        #if they are all gems, add the amount they bet  times 10 to their balance
        await slot_machine.edit(content=f"**{user.name}** won {cash}**{gamble*10}**! \n {slot1} : {slot2} : {slot3}")
        await db_manager.add_money(user.id, gamble*10)
        await db_manager.add_money_earned(user.id, gamble*10)
        
    elif slot1_result == slot2_result == slot3_result == ":crown:":
        #if they are all crowns, add the amount they bet  times 5 to their balance
        await slot_machine.edit(content=f"**{user.name}** won {cash}**{gamble*7.5}**! \n {slot1} : {slot2} : {slot3}")
        await db_manager.add_money(user.id, gamble*8)
        await db_manager.add_money_earned(user.id, gamble*8)
        
    elif slot1_result == slot2_result == slot3_result:
        #if they are the same, add the amount they bet  times 3 to their balance
        await slot_machine.edit(content=f"**{user.name}** won {cash}**{gamble*5}**! \n {slot1} : {slot2} : {slot3}")
        await db_manager.add_money(user.id, gamble*5)
        await db_manager.add_money_earned(user.id, gamble*5)

    else:
        #if they are all different, take the amount they bet from their balance
        await slot_machine.edit(content=f"**{user.name}** lost {cash}**{gamble}**! \n {slot1} : {slot2} : {slot3}")
        #passx
        
#create slots_rules function
#this function will be called when the user types !slots_rules
# /slots_rules will show the rules of the slots game
# /slots_rules will also show the user how to play the slots game
# /slots_rules will also show the user the rewards for each slot
async def slot_rules(ctx: Context):
    #create the embed
    embed = discord.Embed(
        title="Slots Rules",
        description="Slots is a game where you bet money and spin the slots. If the slots are the same, you win money. If the slots are different, you lose money. \n :gem: : :gem: : :gem: | 10x \n :crown: : :crown: : :crown: | 7.5x \n :apple: : :apple: : :apple: | 5x \n :apple: : :apple: : :question: | 3x \n :gem: : :question: : :question: | 1.5x \n :crown: : :question: : :question: | 1.2x",
        color=discord.Color.blue()
    )
    #send the embed
    await ctx.send(embed=embed)
    
class FishingButton(discord.ui.View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @discord.ui.button(label="Continue fishing", style=discord.ButtonStyle.green)
    async def on_continue(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.stop()

async def fishing_game():
    fishes = {
        "Shark": {"emoji": "<:Shark:1107388348693233735>", "points": 10, "rarity": 0.01},
        "Whale": {"emoji": "<:Whale:1107388346264727683>", "points": 9, "rarity": 0.02},
        "Koi": {"emoji": "<:Koi:1107388726985891941>", "points": 8, "rarity": 0.03},
        "Swordfish": {"emoji": "<:Fish_Sword:1107388731599638540>", "points": 7, "rarity": 0.04},
        "Tuna": {"emoji": "<:Fish_Tuna:1107388734682439821>", "points": 6, "rarity": 0.05},
        "Clownfish": {"emoji": "<:Fish_Clown:1107388729930289323>", "points": 5, "rarity": 0.06},
        "Goldfish": {"emoji": "<:Fish_Gold:1107388728839770202>", "points": 4, "rarity": 0.07},
        "Yellow Lab": {"emoji": "<:Fish_LemonYellowLab:1107388730878210129>", "points": 3, "rarity": 0.08},
        "Squid": {"emoji": "<:Cephalopod_Squid:1107389556048793711>", "points": 2, "rarity": 0.09},
        "Octopus": {"emoji": "<:Cephalopod_Octopus:1107389552584294440>", "points": 2, "rarity": 0.1},
        "Dolphin": {"emoji": "<:Mammal_Dolphin:1107389554404622547>", "points": 1, "rarity": 0.11},
        "Crab": {"emoji": "<:Crustacean_Crab:1107389550067720234>", "points": 1, "rarity": 0.12},
        "Jellyfish": {"emoji": "<:Fish_Jellyfish:1107389551758037053>", "points": 1, "rarity": 0.13}
    }

    def catch_fish(user_luck):
        catchable_fishes = [fish for fish in fishes if fishes[fish]["rarity"] <= user_luck/100]
        if not catchable_fishes:
            catchable_fishes = [fish for fish in fishes]
        return random.choice(catchable_fishes)

    async def fish(ctx: Context, user, user_luck):
        points = 0
        tries = 5

        for i in range(tries):
            caught_fish = catch_fish(user_luck)
            fish_points = fishes[caught_fish]["points"]
            points += fish_points

            view = FishingButton()
            await ctx.send(
                content=f'{user.name} caught a {caught_fish} {fishes[caught_fish]["emoji"]} and gained {fish_points} points!',
                view=view
            )

            # Wait for the user to press the button
            await view.wait()

        if points >= 40:
            prize = "Golden Trophy"
        elif points >= 30:
            prize = "Silver Trophy"
        elif points >= 20:
            prize = "Bronze Trophy"
        else:
            prize = "Participation Medal"

        await ctx.send(f'{user.mention} has finished fishing with a total of {points} points and won a {prize}!')

    return fish

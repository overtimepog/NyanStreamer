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
from discord.ui import Button, View, Select

from helpers import db_manager, battle
import asyncio
import os
import random
from io import BytesIO
from random import shuffle
from typing import List, Tuple, Union

import discord
from discord.ext import commands
from helpers.card import Card
from PIL import Image

cash = "⚙"
rarity_colors = {
    "Common": 0x808080,  # Grey
    "Uncommon": 0x319236,  # Green
    "Rare": 0x4c51f7,  # Blue
    "Epic": 0x9d4dbb,  # Purple
    "Legendary": 0xf3af19,  # Gold
    # Add more rarities and colors as needed
}

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
    def __init__(self, user_id, **kwargs):
        super().__init__(**kwargs)
        self.user_id = user_id
        self.button_clicked = asyncio.Event()
        self.selected_spot = None
        self.cancelled = False

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This is not your game!", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="1", style=discord.ButtonStyle.secondary, row=0)
    async def select_spot_1(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.selected_spot = 1
        button.style = discord.ButtonStyle.success
        embed = interaction.message.embeds[0]
        embed.set_footer(text=f"Selected spot: {self.selected_spot}")
        await interaction.message.edit(embed=embed)
        await interaction.response.defer()
        

    @discord.ui.button(label="2", style=discord.ButtonStyle.secondary, row=0)
    async def select_spot_2(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.selected_spot = 2
        button.style = discord.ButtonStyle.success
        embed = interaction.message.embeds[0]
        embed.set_footer(text=f"Selected spot: {self.selected_spot}")
        await interaction.message.edit(embed=embed)
        await interaction.response.defer()

    @discord.ui.button(label="3", style=discord.ButtonStyle.secondary, row=0)
    async def select_spot_3(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.selected_spot = 3
        button.style = discord.ButtonStyle.success
        embed = interaction.message.embeds[0]
        embed.set_footer(text=f"Selected spot: {self.selected_spot}")
        await interaction.message.edit(embed=embed)
        await interaction.response.defer()

    @discord.ui.button(label="4", style=discord.ButtonStyle.secondary, row=1)
    async def select_spot_4(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.selected_spot = 4
        button.style = discord.ButtonStyle.success
        embed = interaction.message.embeds[0]
        embed.set_footer(text=f"Selected spot: {self.selected_spot}")
        await interaction.message.edit(embed=embed)
        await interaction.response.defer()

    @discord.ui.button(label="5", style=discord.ButtonStyle.secondary, row=1)
    async def select_spot_5(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.selected_spot = 5
        button.style = discord.ButtonStyle.success
        embed = interaction.message.embeds[0]
        embed.set_footer(text=f"Selected spot: {self.selected_spot}")
        await interaction.message.edit(embed=embed)
        await interaction.response.defer()

    @discord.ui.button(label="6", style=discord.ButtonStyle.secondary, row=1)
    async def select_spot_6(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.selected_spot = 6
        button.style = discord.ButtonStyle.success
        embed = interaction.message.embeds[0]
        embed.set_footer(text=f"Selected spot: {self.selected_spot}")
        await interaction.message.edit(embed=embed)
        await interaction.response.defer()

    @discord.ui.button(label="7", style=discord.ButtonStyle.secondary, row=2)
    async def select_spot_7(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.selected_spot = 7
        button.style = discord.ButtonStyle.success
        embed = interaction.message.embeds[0]
        embed.set_footer(text=f"Selected spot: {self.selected_spot}")
        await interaction.message.edit(embed=embed)
        await interaction.response.defer()

    @discord.ui.button(label="8", style=discord.ButtonStyle.secondary, row=2)
    async def select_spot_8(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.selected_spot = 8
        button.style = discord.ButtonStyle.success
        embed = interaction.message.embeds[0]
        embed.set_footer(text=f"Selected spot: {self.selected_spot}")
        await interaction.message.edit(embed=embed)
        await interaction.response.defer()

    @discord.ui.button(label="9", style=discord.ButtonStyle.secondary, row=2)
    async def select_spot_9(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.selected_spot = 9
        button.style = discord.ButtonStyle.success
        embed = interaction.message.embeds[0]
        embed.set_footer(text=f"Selected spot: {self.selected_spot}")
        await interaction.message.edit(embed=embed)
        await interaction.response.defer()

    @discord.ui.button(label="Cast", style=discord.ButtonStyle.primary)
    async def cast(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.selected_spot is None:
            await interaction.response.send_message('Please select a fishing spot first!', ephemeral=True)
        else:
            self.button_clicked.set()
            await interaction.response.defer()
            
    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.danger)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.cancelled = True
        self.button_clicked.set()
        await interaction.response.defer()

async def fishing_game():
    fishes = {
    "Shark": {"emoji": "<:Shark:1107388348693233735>", "points": 10, "rarity": 0.01, "rarity_name": "Legendary"},
    "Whale": {"emoji": "<:Whale:1107388346264727683>", "points": 9, "rarity": 0.02, "rarity_name": "Epic"},
    "Koi": {"emoji": "<:Koi:1107388726985891941>", "points": 8, "rarity": 0.03, "rarity_name": "Rare"},
    "Swordfish": {"emoji": "<:Fish_Sword:1107388731599638540>", "points": 7, "rarity": 0.04, "rarity_name": "Rare"},
    "Tuna": {"emoji": "<:Fish_Tuna:1107388734682439821>", "points": 6, "rarity": 0.05, "rarity_name": "Uncommon"},
    "Clownfish": {"emoji": "<:Fish_Clown:1107388729930289323>", "points": 5, "rarity": 0.06, "rarity_name": "Uncommon"},
    "Goldfish": {"emoji": "<:Fish_Gold:1107388728839770202>", "points": 4, "rarity": 0.07, "rarity_name": "Uncommon"},
    "Yellow Lab": {"emoji": "<:Fish_LemonYellowLab:1107388730878210129>", "points": 3, "rarity": 0.08, "rarity_name": "Common"},
    "Squid": {"emoji": "<:Cephalopod_Squid:1107389556048793711>", "points": 2, "rarity": 0.09, "rarity_name": "Common"},
    "Octopus": {"emoji": "<:Cephalopod_Octopus:1107389552584294440>", "points": 2, "rarity": 0.1, "rarity_name": "Common"},
    "Dolphin": {"emoji": "<:Mammal_Dolphin:1107389554404622547>", "points": 1, "rarity": 0.11, "rarity_name": "Common"},
    "Crab": {"emoji": "<:Crustacean_Crab:1107389550067720234>", "points": 1, "rarity": 0.12, "rarity_name": "Common"},
    "Jellyfish": {"emoji": "<:Fish_Jellyfish:1107389551758037053>", "points": 1, "rarity": 0.13, "rarity_name": "Common"}
    }

    rarity_colors = {
        "Common": 0x808080,  # Grey
        "Uncommon": 0x319236,  # Green
        "Rare": 0x4c51f7,  # Blue
        "Epic": 0x9d4dbb,  # Purple
        "Legendary": 0xf3af19,  # Gold
    }

    def catch_fish(user_luck):
        catchable_fishes = [fish for fish in fishes if fishes[fish]["rarity"] <= user_luck/100]
        if not catchable_fishes:
            catchable_fishes = [fish for fish in fishes]
        return random.choice(catchable_fishes)

    async def fish(ctx: Context, user, user_luck):
        baitAmount = await db_manager.get_item_amount_from_inventory(user.id, "bait")
        points = 0
        tries = 5 + baitAmount

        view = FishingButton(user.id)
        message = None

        instructions = (
            "Welcome to the fishing game! Here's how to play:\n"
            "1. Select a fishing spot by clicking on one of the numbered buttons.\n"
            "2. After selecting a panel, click the 'Cast' button to fish.\n"
            "3. Repeat this process until you've used all your bait.\n"
            "Good luck!"
        )

        embed = discord.Embed(
            title=f"{user.name}'s Fishing Game",
            description=instructions + "\n" + "\n" + f"Starting Bait: {tries}",
            color=0x00BFFF  # Light blue
        )
        
        message = await ctx.send(embed=embed, view=view)

        await view.button_clicked.wait()

        for i in range(tries):
            if view.cancelled:
                break

            if view.selected_spot is None:
                await ctx.send("Please select a fishing spot first!")
                return

            await view.button_clicked.wait()
            view.button_clicked.clear()

            caught_fish = catch_fish(user_luck)
            fish_points = fishes[caught_fish]["points"]
            points += fish_points

            embed = discord.Embed(
                title=f'{user.name} caught a {fishes[caught_fish]["emoji"]}{caught_fish} in spot {view.selected_spot}!',
                description=f'gained {fish_points} points! Bait left: {tries - i - 1}',
                color=rarity_colors[fishes[caught_fish]["rarity_name"]]
            )
            embed.set_footer(text=f"Selected spot: {view.selected_spot}")

            await message.edit(embed=embed)

            if baitAmount > 0:
                await db_manager.remove_item_from_inventory(user.id, "bait", 1)
                baitAmount -= 1
            
        if baitAmount == 0:
            if points >= 60:
                prizeID = "fish_pet_epic"
                prizeName = await db_manager.get_basic_item_name(prizeID)
                prizeEmoji = await db_manager.get_basic_item_emoji(prizeID)
                prizeAmount = 1
                prize = f"{prizeEmoji} {prizeName} x{prizeAmount}"
                if view.cancelled:
                    await ctx.send(f'{user.mention} has finished fishing. Total points: {points}. You won {prize}!')
                    await db_manager.add_item_to_inventory(user.id, prizeID, 1)
                else:
                    await ctx.send(f'{user.mention} has finished fishing. Total points: {points}. You won {prize}!')
                    await db_manager.add_item_to_inventory(user.id, prizeID, 1)
            elif points >= 45:
                prizeID = "pet_chest"
                prizeName = await db_manager.get_chest_name(prizeID)
                prizeEmoji = await db_manager.get_chest_icon(prizeID)
                prizeAmount = 1
                prize = f"{prizeEmoji} {prizeName} x{prizeAmount}"
                if view.cancelled:
                    await ctx.send(f'{user.mention} has finished fishing. Total points: {points}. You won {prize}!')
                    await db_manager.add_item_to_inventory(user.id, prizeID, 1)
                else:
                    await ctx.send(f'{user.mention} has finished fishing. Total points: {points}. You won {prize}!')
                    await db_manager.add_item_to_inventory(user.id, prizeID, 1)
            elif points >= 30:
                prizeID = "chest"
                prizeName = await db_manager.get_chest_name(prizeID)
                prizeEmoji = await db_manager.get_chest_icon(prizeID)
                prizeAmount = 2
                prize = f"{prizeEmoji} {prizeName} x{prizeAmount}"
                if view.cancelled:
                    await ctx.send(f'{user.mention} has finished fishing. Total points: {points}. You won {prize}!')
                    await db_manager.add_item_to_inventory(user.id, prizeID, 2)
                else:
                    await ctx.send(f'{user.mention} has finished fishing. Total points: {points}. You won {prize}!')
                    await db_manager.add_item_to_inventory(user.id, prizeID, 2)
            elif points >= 15:
                prizeID = "chest"
                prizeName = await db_manager.get_chest_name(prizeID)
                prizeEmoji = await db_manager.get_chest_icon(prizeID)
                prizeAmount = 1
                prize = f"{prizeEmoji} {prizeName} x{prizeAmount}"
                if view.cancelled:
                    await ctx.send(f'{user.mention} has finished fishing. Total points: {points}. You won {prize}!')
                    await db_manager.add_item_to_inventory(user.id, prizeID, 1)
                else:
                    await ctx.send(f'{user.mention} has finished fishing. Total points: {points}. You won {prize}!')
                    await db_manager.add_item_to_inventory(user.id, prizeID, 1)
            elif points >= 5:
                prizeID = "bait"
                prizeName = await db_manager.get_basic_item_name(prizeID)
                prizeEmoji = await db_manager.get_basic_item_emoji(prizeID)
                prizeAmount = 2
                prize = f"{prizeEmoji} {prizeName} x{prizeAmount}"
                if view.cancelled:
                    await ctx.send(f'{user.mention} has finished fishing. Total points: {points}. You won {prize}!')
                    await db_manager.add_item_to_inventory(user.id, prizeID, 2)
                else:
                    await ctx.send(f'{user.mention} has finished fishing. Total points: {points}. You won {prize}!')
                    await db_manager.add_item_to_inventory(user.id, prizeID, 2)
    return fish


class TriviaButton(Button):
    def __init__(self, label, trivia_view, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label = label
        self.trivia_view = trivia_view

    async def callback(self, interaction: discord.Interaction):
        selected_choice = self.label
        if selected_choice == self.trivia_view.answer:
            color = discord.Color.green()
            text = f"Correct! The answer was {self.trivia_view.answer}."
            self.style = discord.ButtonStyle.success
            #give the user a prize and some xp
            #decide if the user is gonna get a chest or pet chest
            random_number = random.randint(1, 100)
            if random_number <= 5:
                await db_manager.add_item_to_inventory(interaction.user.id, "pet_chest", 1)
                await db_manager.add_xp(interaction.user.id, 50)
                pet_chest_emoji = await db_manager.get_chest_icon("pet_chest")
                await interaction.message.reply(f"{interaction.user.mention} got a {pet_chest_emoji}Pet Chest and ⭐50 xp!")
                canLevelUp = await db_manager.can_level_up(interaction.user.id)
                if canLevelUp:
                    await db_manager.add_level(interaction.user.id, 1)
                    new_level = await db_manager.get_level(interaction.user.id)
                    await interaction.message.reply(f"{interaction.user.mention} has leveled up! They are now level " + str(new_level) + "!")
            else:
                await db_manager.add_item_to_inventory(interaction.user.id, "chest", 1)
                await db_manager.add_xp(interaction.user.id, 10)
                chest_emoji = await db_manager.get_chest_icon("chest")
                await interaction.message.reply(f"{interaction.user.mention} got a {chest_emoji}Chest and ⭐10 xp!")
                #check if the user can level up 
                canLevelUp = await db_manager.can_level_up(interaction.user.id)
                if canLevelUp:
                    await db_manager.add_level(interaction.user.id, 1)
                    new_level = await db_manager.get_level(interaction.user.id)
                    await interaction.message.reply(f"{interaction.user.mention} has leveled up! They are now level " + str(new_level) + "!")



        else:
            color = discord.Color.red()
            text = f"Sorry, that's incorrect. The correct answer was {self.trivia_view.answer}."
            self.style = discord.ButtonStyle.danger

        embed = interaction.message.embeds[0]
        embed.color = color
        embed.set_footer(text=text)
        await interaction.message.edit(embed=embed, view=None)

class TriviaView(View):
    def __init__(self, answer, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.answer = answer

    def add_choice(self, choice):
        self.add_item(TriviaButton(label=choice, trivia_view=self, style=discord.ButtonStyle.secondary))


async def trivia(self, ctx: commands.Context):
        def load_questions(filename):
            with open(filename, 'r') as file:
                data = json.load(file)
            return data

        math = load_questions('assets/items/puzzles/math.json')
        random_math_question = random.choice(math['mathPuzzles'])
        math_problem = random_math_question['problem']
        math_choices = random_math_question['choices']
        math_answer = random_math_question['answer']

        riddles = load_questions('assets/items/puzzles/riddles.json')
        random_riddle_question = random.choice(riddles['riddles'])
        riddle = random_riddle_question['riddle']
        riddle_choices = random_riddle_question['choices']
        riddle_answer = random_riddle_question['answer']

        sequences = load_questions('assets/items/puzzles/sequence.json')
        random_sequence_question = random.choice(sequences['sequencePuzzles'])
        sequence = random_sequence_question['sequence']
        sequence_choices = random_sequence_question['choices']
        sequence_answer = random_sequence_question['answer']

        word_puzzles = load_questions('assets/items/puzzles/word.json')
        random_word_question = random.choice(word_puzzles['wordPuzzles'])
        word_problem = random_word_question['problem']
        word_choices = random_word_question['choices']
        word_answer = random_word_question['answer']

        # Load the logic puzzles
        logic_puzzles = load_questions('assets/items/puzzles/logic.json')
        random_logic_question = random.choice(logic_puzzles['logicPuzzles'])
        logic_problem = random_logic_question['problem']
        logic_choices = random_logic_question['choices']
        logic_answer = random_logic_question['answer']

        puzzles = [
            {"type": "Math Problem", "question": math_problem, "choices": math_choices, "answer": math_answer},
            {"type": "Riddle", "question": riddle, "choices": riddle_choices, "answer": riddle_answer},
            {"type": "Sequence", "question": sequence, "choices": sequence_choices, "answer": sequence_answer},
            {"type": "Word Puzzle", "question": word_problem, "choices": word_choices, "answer": word_answer},
            {"type": "Logic Puzzle", "question": logic_problem, "choices": logic_choices, "answer": logic_answer}
        ]

        selected_puzzle = random.choice(puzzles)

        embed = Embed(
            title=f"{selected_puzzle['type']}",
            description=f"{selected_puzzle['question']}",
            color=discord.Color.blue()
        )

        view = TriviaView(selected_puzzle['answer'])

        for choice in selected_puzzle['choices']:
            view.add_choice(choice)

        await ctx.send(embed=embed, view=view)

# -------------------- for WORK COMMAND --------------------

class TriviaGameView(View):
    def __init__(self, answer, resolve_callback, callback_processed_future, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.answer = answer
        self.resolve_callback = resolve_callback
        self.callback_processed_future = callback_processed_future
        self.user = user

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id == self.user.id:
            return True
        return False

    def add_choice(self, choice):
        self.add_item(TriviaGameButton(label=choice, trivia_view=self, callback_processed_future=self.callback_processed_future, style=discord.ButtonStyle.secondary))

class TriviaGameButton(Button):
    def __init__(self, label, trivia_view, callback_processed_future, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label = label
        self.trivia_view = trivia_view
        self.callback_processed_future = callback_processed_future

    async def callback(self, interaction: discord.Interaction):
        self.disabled = True
        selected_choice = self.label
        if selected_choice == self.trivia_view.answer:
            self.style = discord.ButtonStyle.success
            self.trivia_view.resolve_callback.set_result(True)
            await interaction.response.defer()
        else:
            self.style = discord.ButtonStyle.danger
            self.trivia_view.resolve_callback.set_result(False)
            await interaction.response.defer()

        # Set callback_processed_future result here
        self.callback_processed_future.set_result(True)
        await interaction.response.defer()

async def play_trivia(ctx, game_data, minigameText, callback_processed_future):
    random_trivia = random.choice(game_data)
    trivia_question = random_trivia[1]  # accessing the second element of tuple
    trivia_choices = json.loads(random_trivia[2])  # accessing the third element of tuple
    trivia_answer = random_trivia[3]

    resolve_promise = ctx.bot.loop.create_future()

    view = TriviaGameView(answer=trivia_answer, resolve_callback=resolve_promise, callback_processed_future=callback_processed_future, user=ctx.author)

    random.shuffle(trivia_choices)  # Shuffle the choices

    for choice in trivia_choices:
        view.add_choice(choice)

    sendingMessage = minigameText + "\n" + f"`{trivia_question}`"

    message = await ctx.send(content=sendingMessage, view=view)
    try:
        result = await asyncio.wait_for(resolve_promise, timeout=60.0)
    except asyncio.TimeoutError:
        await ctx.send("Time's up!")
        result = False

    return result, message

class OrderGameSelect(Select):
    def __init__(self, correct_order, resolve_callback, callback_processed_future, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.correct_order = correct_order
        self.resolve_callback = resolve_callback
        self.callback_processed_future = callback_processed_future

    async def callback(self, interaction: discord.Interaction):
        user_order = self.values

        if user_order == self.correct_order:
            self.resolve_callback.set_result(True)
            await interaction.response.defer()
        else:
            self.resolve_callback.set_result(False)
            await interaction.response.defer()

        self.callback_processed_future.set_result(True)
        await interaction.response.defer()

async def play_order_game(ctx, game_data, minigameText, callback_processed_future):
    game = random.choice(game_data)
    correct_order = json.loads(game[1])  # accessing the second element of tuple
    items = json.loads(game[2])

    resolve_promise = ctx.bot.loop.create_future()
    select_menu = OrderGameSelect(correct_order=correct_order, resolve_callback=resolve_promise, callback_processed_future=callback_processed_future, placeholder="Select the correct order", max_values=len(items), options=[discord.SelectOption(label=item, value=item) for item in items])

    view = View()
    view.add_item(select_menu)

    sendingMessage = minigameText + "\n" + game["task"]
    message = await ctx.send(content=sendingMessage, view=view)

    try:
        result = await asyncio.wait_for(resolve_promise, timeout=60.0)
    except asyncio.TimeoutError:
        await ctx.send("Time's up!")
        result = False

    return result, message

class MatchingGameSelect(Select):
    def __init__(self, correct_match, resolve_callback, callback_processed_future, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.correct_match = correct_match
        self.resolve_callback = resolve_callback
        self.callback_processed_future = callback_processed_future

    async def callback(self, interaction: discord.Interaction):
        user_match = self.values[0]

        if user_match == self.correct_match:
            self.resolve_callback.set_result(True)
            await interaction.response.defer()
        else:
            self.resolve_callback.set_result(False)
            await interaction.response.defer()

        self.callback_processed_future.set_result(True)
        await interaction.response.defer()

async def play_matching_game(ctx, game_data, minigameText, callback_processed_future):
    game = random.choice(game_data)
    items = json.loads(game[1])  # accessing the second element of tuple
    correct_matches = json.loads(game[2])

    target = random.choice(items)

    correct_description = [item['description'] for item in correct_matches if item['name'] == target['name']][0]

    other_descriptions = [item['description'] for item in items if item['name'] != target['name']]
    random.shuffle(other_descriptions)
    descriptions = [correct_description] + other_descriptions[:3]
    random.shuffle(descriptions)

    resolve_promise = ctx.bot.loop.create_future()
    select_menu = MatchingGameSelect(correct_match=correct_description, resolve_callback=resolve_promise, callback_processed_future=callback_processed_future, placeholder="Match the item", options=[discord.SelectOption(label=desc, value=desc) for desc in descriptions])

    view = discord.ui.View()
    view.add_item(select_menu)

    sendingMessage = minigameText + "\n" + "Match the item: " + target['name']
    message = await ctx.send(content=sendingMessage, view=view)

    try:
        result = await asyncio.wait_for(resolve_promise, timeout=60.0)
    except asyncio.TimeoutError:
        await ctx.send("Time's up!")
        result = False

    return result, message

class ChoiceGameButton(Button):
    def __init__(self, label, resolve_callback, callback_processed_future, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label = label
        self.resolve_callback = resolve_callback
        self.callback_processed_future = callback_processed_future

    async def callback(self, interaction: discord.Interaction):
        self.resolve_callback.set_result(self.label)  # Return the label of the selected option
        self.callback_processed_future.set_result(True)
        await interaction.response.defer()

class ChoiceGameView(View):
    def __init__(self, resolve_callback, callback_processed_future, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.resolve_callback = resolve_callback
        self.callback_processed_future = callback_processed_future
        self.user = user

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id == self.user.id:
            return True
        return False

    def add_choice(self, choice):
        self.add_item(ChoiceGameButton(label=choice, resolve_callback=self.resolve_callback, callback_processed_future=self.callback_processed_future, style=discord.ButtonStyle.secondary))

async def play_choice_game(ctx, game_data, minigameText, callback_processed_future):
    prompt = game_data[0]['minigame_id']

    resolve_promise = ctx.bot.loop.create_future()
    view = ChoiceGameView(resolve_callback=resolve_promise, callback_processed_future=callback_processed_future, user=ctx.author)

    for game_option in game_data:
        view.add_choice(game_option['description'])

    sendingMessage = minigameText + "\n" + "Choose your action"
    message = await ctx.send(content=sendingMessage, view=view)

    try:
        result = await asyncio.wait_for(resolve_promise, timeout=60.0)
        game_outcomes = next((option['outcomes'] for option in game_data if option['description'] == result), None)
    except asyncio.TimeoutError:
        await ctx.send("Time's up!")
        result = False
        game_outcomes = None

    return result, game_outcomes, message

#catch the fish minigame

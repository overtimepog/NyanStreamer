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
from typing import List, Tuple
cash = "⚙"

class SearchButton(discord.ui.Button['SearchButton']):
    def __init__(self, label: str, location: dict, user: discord.User):
        super().__init__(style=discord.ButtonStyle.primary, label=label)
        self.location = location
        self.user = user

    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.user:
            await interaction.response.send_message("These buttons are not for you!", ephemeral=True)
            return

        # Disable all the buttons once one has been clicked
        for item in self.view.children:
            item.disabled = True

        # Update the original message to reflect the disabled buttons
        await interaction.message.edit(view=self.view)

        comment_types = ["positive_comments", "negative_comments"] * 10 + ["death_comments"]
        comment_type = random.choice(comment_types)
        comment = random.choice(self.location[comment_type])

        print("Chosen Comment Type: " + comment_type + "\nChosen Comment: " + comment)
        #change the embed based on the comment type
        if comment_type == "positive_comments":
            bonus = await db_manager.get_percent_bonus(self.user.id)
            bonus_money = int(bonus * 5000)
            total = 5000 + bonus_money
            await db_manager.add_money(self.user.id, total)
            comment = str(comment)
            #replace the {thing} in the comment with the user's money
            comment = comment.replace("{thing}", f"**{cash}{total}**")
            
            embed = discord.Embed(description=comment)
            embed.set_footer(text=f'Bonus +{bonus}% ({cash}{bonus_money})')
            #give the user money
            #get the bonus percentage of the user
            
    
            # Add item finding mechanism here
            firsthuntitems = await db_manager.view_huntable_items()
            huntItems = []
            for item in firsthuntitems:
                item_id = item[0]
                hunt_chance = item[16]
                huntItems.append([item_id, hunt_chance])
    
            luck = await db_manager.get_luck(interaction.user.id)
            huntItems = [(item, chance + luck / 100) for item, chance in huntItems]
            total_chance = sum(chance for item, chance in huntItems)
            huntItems = [(item, chance / total_chance) for item, chance in huntItems]
    
            item = choose_item_based_on_hunt_chance(huntItems)
    
            if item is not None:
                amount = random.randint(1, 5)
                amount = amount + (luck // 10)
                if amount < 1:
                    amount = 1
                if amount > 10:
                    amount = 10
    
                await db_manager.add_item_to_inventory(interaction.user.id, item, amount)
                item_id = item
                item_id = str(item_id)
    
                if item_id.split("_")[0] == "chest" or item_id == "chest":
                    item_emoji = await db_manager.get_chest_icon(item_id)
                    item_name = await db_manager.get_chest_name(item_id)
                else:
                    item_emoji = await db_manager.get_basic_item_emoji(item_id)
                    item_name = await db_manager.get_basic_item_name(item_id)
    
                embed.description += f"\nDang lucky you, you found x{amount} {item_emoji}{item_name}!"
            
        embed.set_author(name=self.user.display_name + f" Searched {self.label}", icon_url=self.user.avatar.url)
        await interaction.response.send_message(embed=embed)

def choose_item_based_on_hunt_chance(items_with_chances: List[Tuple]):
    total = sum(w for i, w in items_with_chances)
    r = random.uniform(0, total)
    upto = 0
    for item, w in items_with_chances:
        if upto + w >= r:
            return item
        upto += w
    assert False, "Shouldn't get here"

class SearchLocationButton(discord.ui.View):
    def __init__(self, locations, user):
        super().__init__()
        for location in locations:
            self.add_item(SearchButton(location['location'], location, user))


async def search(ctx: Context):
    userGain = 5000
    with open('assets/search.json') as f:
        data = json.load(f)
        locations = data['searches']

    selected_locations = random.sample(locations, 3)
    view = SearchLocationButton(selected_locations, ctx.author)
    embed = discord.Embed(title="Search", description="Choose a location to search:", color=discord.Color.blue())
    embed.set_footer(text=f'Search initiated by {ctx.author.display_name}', icon_url=ctx.author.avatar.url)
    await ctx.send(embed=embed, view=view)

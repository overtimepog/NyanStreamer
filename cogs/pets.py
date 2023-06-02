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
from discord.ext.commands import Context, has_permissions, Bot

from helpers import battle, checks, db_manager, hunt, mine
from typing import List, Tuple
from discord.ext.commands.errors import CommandInvokeError


cash = "<:cash:1077573941515792384>"
rarity_colors = {
    "Common": 0x808080,  # Grey
    "Uncommon": 0x319236,  # Green
    "Rare": 0x4c51f7,  # Blue
    "Epic": 0x9d4dbb,  # Purple
    "Legendary": 0xf3af19,  # Gold
}

class PetSelect(discord.ui.Select):
    def __init__(self, pets: list, bot):
        self.bot = bot
        self.pets = pets
        self.selected_pet = None
        #print(self.pets)
        super().__init__(placeholder='Select your pet...', min_values=1, max_values=1)

    async def prepare_options(self):
        options = []
        for pet in self.pets:
            #print(pet)
            pet_emoji = await db_manager.get_basic_item_emote(pet[0])
            petitemname = await db_manager.get_basic_item_name(pet[0])
            options.append(discord.SelectOption(label=pet[2], value=pet[0], emoji=pet_emoji, description=f"Level {pet[3]} {petitemname}"))
        self.options = options

    async def callback(self, interaction: discord.Interaction):
        self.view.value = self.values[0]
        self.selected_pet = await db_manager.get_pet_attributes(interaction.user.id, self.values[0])  # Update instance attribute
        embed = await create_pet_embed(self.selected_pet)
        await interaction.response.edit_message(embed=embed)
        await interaction.response.defer()
        await self.prepare_options()


class PetSelectView(discord.ui.View):
    def __init__(self, pets: list, user: discord.User, bot):
        super().__init__()
        self.user = user
        self.value = None
        self.select = PetSelect(pets, bot)
        self.add_item(self.select)

    async def prepare(self):
        await self.select.prepare_options()

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return self.user.id == interaction.user.id


async def create_pet_embed(pet):
    rarity = await db_manager.get_basic_item_rarity(pet[0])
    embed = discord.Embed(
        title=f"{pet[2]}'s Statistics",
        description=f"This is the stats of your pet {pet[2]}",
        color=rarity_colors[rarity]
    )
    embed.add_field(name="Level", value=pet[3], inline=True)
    embed.add_field(name="XP", value=pet[4], inline=True)
    #create the bar
    embed.add_field(name="Hunger", value=generate_progress_bar(pet[5], 100), inline=True)
    embed.add_field(name="Cleanliness", value=generate_progress_bar(pet[6], 100), inline=True)
    embed.add_field(name="Happiness", value=generate_progress_bar(pet[7], 100), inline=True)
    #hungry = pet[5]
    #clean = pet[6]
    #happy = pet[7]
    #generate a bar for each stat

    # Add more stats as needed
    return embed

def generate_progress_bar(value, max_value):
    # Number of total parts in the bar.
    TOTAL_PARTS = 10

    # Calculate how many parts should be filled.
    filled_parts = round((value / max_value) * TOTAL_PARTS)

    # Create the bar.
    bar = '▰' * filled_parts + '▱' * (TOTAL_PARTS - filled_parts)

    return bar

class Pets(commands.Cog, name="pets"):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command()
    async def pet(self, ctx: Context):
        """Display your pet's stats."""
        pets = await db_manager.get_users_pets(ctx.author.id)
        if not pets:
            await ctx.send('You do not own any pets.')
            return

        view = PetSelectView(pets, ctx.author, self.bot)
        await view.prepare()
        message = await ctx.send('Select a Pet :)', view=view)
        view.message = message

async def setup(bot):
    await bot.add_cog(Pets(bot))
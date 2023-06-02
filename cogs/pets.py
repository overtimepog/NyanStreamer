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
from discord.ext import tasks

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
        super().__init__(placeholder='Select your pet...', min_values=1, max_values=1)

    async def prepare_options(self):
        options = []
        for pet in self.pets:
            pet_emoji = await db_manager.get_basic_item_emote(pet[0])
            petitemname = await db_manager.get_basic_item_name(pet[0])
            options.append(discord.SelectOption(label=pet[2], value=pet[0], emoji=pet_emoji, description=f"Level {pet[3]} {petitemname}"))
        self.options = options

    async def callback(self, interaction: discord.Interaction):
        self.view.value = self.values[0]
        self.selected_pet = await db_manager.get_pet_attributes(interaction.user.id, self.values[0])  # Update instance attribute
        embed = await create_pet_embed(self.selected_pet)
        await interaction.response.edit_message(embed=embed)
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

def calculate_time_till_empty(current_value, decrease_rate, loop_interval):
    """Calculate the time until the attribute reaches zero."""
    if current_value <= 0:
        return "Already empty"
    else:
        remaining_loops = current_value // decrease_rate
        remaining_time = remaining_loops * loop_interval  # in minutes

        hours, remainder = divmod(remaining_time, 60)
        minutes, seconds = divmod(remainder, 1)

        if hours > 0:
            return f"{int(hours)}hr"
        elif minutes > 0:
            return f"{int(minutes)}m"
        else:
            return f"{int(seconds)}s"

def generate_progress_bar(value, max_value):
    TOTAL_PARTS = 10
    filled_parts = round((value / max_value) * TOTAL_PARTS)
    bar = '▰' * filled_parts + '▱' * (TOTAL_PARTS - filled_parts)

    return bar

async def create_pet_embed(pet):
    rarity = await db_manager.get_basic_item_rarity(pet[0])
    icon = await db_manager.get_basic_item_emote(pet[0])
    embed = discord.Embed(
        title=f"{pet[2]}'s Statistics",
        description=f"This is the stats of your pet {pet[2]}",
        color=rarity_colors[rarity]
    )
    embed.set_thumbnail(url=f"https://cdn.discordapp.com/emojis/{icon.split(':')[2].replace('>', '')}.gif?size=240&quality=lossless")
    embed.add_field(name="Level", value=pet[3], inline=True)
    embed.add_field(name="XP", value=pet[4], inline=True)
    embed.add_field(name=f"Hunger `{pet[5]}/100`", value="```" + generate_progress_bar(pet[5], 100) + "```\n<sub>Time till empty: {calculate_time_till_empty(pet[5], 5, 30)}</sub>", inline=False)
    embed.add_field(name=f"Cleanliness `{pet[6]}/100`", value="```" + generate_progress_bar(pet[6], 100) + "```\n<sub>Time till empty: {calculate_time_till_empty(pet[6], 5, 120)}</sub>", inline=False)
    embed.add_field(name=f"Happiness `{pet[7]}/100`", value="```" + generate_progress_bar(pet[7], 100) + "```\n<sub>Time till empty: {calculate_time_till_empty(pet[7], 5, 60)}</sub>", inline=False)

    return embed

class Pets(commands.Cog, name="pets"):
    def __init__(self, bot):
        self.bot = bot
        self.update_pet_hunger.start()
        self.update_pet_happiness.start()
        self.update_pet_cleanliness.start()

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

    @tasks.loop(minutes=30)
    async def update_pet_hunger(self):
        """Update pets' hunger periodically."""
        all_pets = await db_manager.get_all_users_pets()
        for pet in all_pets:
            await db_manager.remove_pet_hunger(pet[1], pet[0], 5)
            updated = await db_manager.get_pet_attributes(pet[1], pet[0])
            print(f'Updated hunger for {pet[1]}' + f'\'s pet {pet[2]}, It is now {updated[5]}')

    @update_pet_hunger.before_loop
    async def before_update_hunger(self):
        await self.bot.wait_until_ready()

    @tasks.loop(hours=1)
    async def update_pet_happiness(self):
        """Update pets' happiness periodically."""
        all_pets = await db_manager.get_all_users_pets()
        for pet in all_pets:
            await db_manager.remove_pet_happiness(pet[1], pet[0], 5)
            updated = await db_manager.get_pet_attributes(pet[1], pet[0])
            print(f'Updated happiness for {pet[1]}' + f'\'s pet {pet[2]}, It is now {updated[7]}')

    @update_pet_happiness.before_loop
    async def before_update_happiness(self):
        await self.bot.wait_until_ready()

    @tasks.loop(hours=2)
    async def update_pet_cleanliness(self):
        """Update pets' cleanliness periodically."""
        all_pets = await db_manager.get_all_users_pets()
        for pet in all_pets:
            await db_manager.remove_pet_cleanliness(pet[1], pet[0], 5)
            updated = await db_manager.get_pet_attributes(pet[1], pet[0])
            print(f'Updated cleanliness for {pet[1]}' + f'\'s pet {pet[2]}, It is now {updated[6]}')

    @update_pet_cleanliness.before_loop
    async def before_update_cleanliness(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(Pets(bot))

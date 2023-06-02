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
    def __init__(self, pets: list):
        options = []
        for pet in pets:
            pet_emoji = bot.loop.run_until_complete(db_manager.get_basic_item_emote(pet[0]))
            options.append(discord.SelectOption(label=pet[2], value=pet[0], emoji=pet_emoji))
        super().__init__(placeholder='Select your pet...', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        self.view.value = self.values[0]
        selected_pet = await db_manager.get_pet(self.values[0])
        embed = await create_pet_embed(selected_pet)
        await interaction.response.edit_message(embed=embed)
        self.view.stop()

class PetSelectView(discord.ui.View):
    def __init__(self, pets: list, user: discord.User):
        super().__init__()
        self.user = user
        self.value = None
        self.add_item(PetSelect(pets))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return self.user.id == interaction.user.id

    async def on_timeout(self) -> None:
        for item in self.children:
            item.disabled = True
        await self.message.edit(view=self)


async def create_pet_embed(pet):
    rarity = await db_manager.get_basic_item_rarity(pet[0])
    embed = discord.Embed(
        title=f"{pet['pet_name']}'s Statistics",
        description=f"This is the stats of your pet {pet['pet_name']}",
        color=rarity_colors[rarity]
    )
    embed.add_field(name="Level", value=pet[3], inline=True)
    embed.add_field(name="XP", value=pet[4], inline=True)
    # Add more stats as needed
    return embed


class Pets(commands.Cog, name="pets"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def pet(self, ctx: Context):
        """Display your pet's stats."""
        pets = await db_manager.get_users_pets(ctx.author.id)
        if not pets:
            await ctx.send('You do not own any pets.')
            return

        view = PetSelectView(pets, ctx.author)
        message = await ctx.send('Select a pet to see its stats:', view=view)
        view.message = message

async def setup(bot):
    await bot.add_cog(Pets(bot))
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
    # Add more rarities and colors as needed
}
class PetSelect(discord.ui.Select):
    def __init__(self, pets: list):
        options = []
        for pet in pets:
            options.append(discord.SelectOption(label=pet['pet_name'], value=pet['item_id']))
        super().__init__(placeholder='Select your pet...', min_values=1, max_values=1, options=options)
    async def callback(self, interaction: discord.Interaction):
        self.view.value = self.values[0]
        await interaction.response.send_message(f"You've selected {self.values[0]}", ephemeral=True)
        self.view.stop()

class PetSelectView(discord.ui.View):
    def __init__(self, pets: list):
        super().__init__()
        self.value = None
        self.add_item(PetSelect(pets))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return self.user.id == interaction.user.id

    async def on_timeout(self) -> None:
        for item in self.children:
            item.disabled = True
        await self.message.edit(view=self)

# Here we name the cog and create a new class for the cog.
class Pets(commands.Cog, name="pets"):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_group(invoke_without_command=True)
    async def pet(self, ctx):
        """The parent pet command."""
        await ctx.send('This is the parent pet command. Use `d.help pet` for more options.')

    @pet.command(
            name="feed",
            aliases=["eat"],
            description="Feed your pet.",
    )
    async def feed(self, ctx):
        """Feed your pet."""
        await ctx.send('You fed your pet!')
        return

    @pet.command(
            name="level",
            aliases=["lvl"],
            description="Shows the level of your pet",
    )
    async def level(self, ctx):
        """Shows the level of your pet. Only for bot owner."""
        await ctx.send('Your pet is at level 1.')


    @pet.command(
        name="name",
        aliases=["rename"],
        description="Name your pet.",
    )
    async def name(self, ctx: Context, new_name: str):
        """Name your pet."""

        pets = await db_manager.get_users_pets(ctx.author.id)
        if not pets:
            await ctx.send('You do not own any pets.')
            return

        view = PetSelectView(pets)
        message = await ctx.send('Select the pet you want to rename:', view=view)
        view.message = message
        await view.wait()

        if view.value:
            await db_manager.rename_pet(ctx.author.id, view.value, new_name)
            await ctx.send(f'You named your pet {new_name}!')
        else:
            await ctx.send('You did not select any pet.')
    
    # You can add more pet-related commands here

async def setup(bot):
    await bot.add_cog(Pets(bot))